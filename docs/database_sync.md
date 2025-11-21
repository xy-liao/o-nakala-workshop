# Database Synchronization

**Advanced Topic**: Understanding NAKALA's dual database architecture.

---

## 🏗️ NAKALA's Storage Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NAKALA API                              │
│                    (Symfony Framework)                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   MariaDB (SQL)  │  │ GraphDB (RDF)    │  │   NAS Storage    │
│                  │  │                  │  │                  │
│ • Metadata       │  │ • RDF Triples    │  │ • Binary Files   │
│ • Relations      │  │ • Ontology       │  │ • Images, PDFs   │
│ • User rights    │  │ • Semantic links │  │ • Videos, etc.   │
│ • Fast queries   │  │ • Advanced search│  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Key Point**: MariaDB and GraphDB must stay **perfectly synchronized** at all times.

---

## Why Two Databases?

### MariaDB (SQL)
- **Fast relational queries**
- **ACID guarantees**
- **Easy to update specific rows**

### GraphDB (RDF)
- **Semantic web compatibility**
- **SPARQL queries**
- **Ontology-based reasoning**

---

## The PATCH Problem

### In SQL (MariaDB) - Partial Updates Are Easy

```sql
-- Update ONLY the French title
UPDATE metadata
SET value = 'Nouveau titre'
WHERE dataset_id = '123'
  AND property = 'title'
  AND language = 'fr';

-- ✅ Other titles (English, Spanish) remain untouched
-- ✅ Other metadata fields remain untouched
```

**SQL tables store data in rows/columns** → Easy to update specific cells.

---

### In RDF (GraphDB) - Everything is a Triple

**RDF stores data as atomic triplets** (subject-predicate-object):

```
┌────────────────────────────────────────────────┐
│ Subject          Predicate      Object         │
├────────────────────────────────────────────────┤
│ nakala:abc123 → nakala:title → "Mon titre"@fr │
│ nakala:abc123 → nakala:title → "My title"@en  │
│ nakala:abc123 → nakala:type  → coar:image     │
└────────────────────────────────────────────────┘
```

**To modify a triple in SPARQL**:

```sparql
# Step 1: DELETE the old triple
DELETE {
  nakala:abc123 nakala:title "Mon titre"@fr
}

# Step 2: INSERT the new triple
INSERT {
  nakala:abc123 nakala:title "Nouveau titre"@fr
}

WHERE {
  nakala:abc123 nakala:title "Mon titre"@fr
}
```

**Problem**: You can't UPDATE a triple - you must **DELETE + INSERT** (atomic replacement).

---

## The Ambiguity Problem

### Scenario: Multilingual Metadata

**Current state**:
```json
{
  "title": [
    {"value": "Mon titre", "lang": "fr"},
    {"value": "My title", "lang": "en"},
    {"value": "Mi título", "lang": "es"}
  ]
}
```

**User sends PATCH**:
```json
{
  "title": {"value": "Nouveau titre", "lang": "fr"}
}
```

### ❓ What Should Happen?

**Option 1**: Replace ONLY French title (surgical update)
```json
{
  "title": [
    {"value": "Nouveau titre", "lang": "fr"},  // ✅ Updated
    {"value": "My title", "lang": "en"},       // ✅ Preserved
    {"value": "Mi título", "lang": "es"}       // ✅ Preserved
  ]
}
```

**Option 2**: Replace ALL titles (total replacement)
```json
{
  "title": [
    {"value": "Nouveau titre", "lang": "fr"}   // ✅ Updated
    // ❌ English and Spanish lost!
  ]
}
```

**Option 3**: Merge/Append (add new title)
```json
{
  "title": [
    {"value": "Mon titre", "lang": "fr"},      // ❌ Duplicate!
    {"value": "Nouveau titre", "lang": "fr"},  // ✅ New
    {"value": "My title", "lang": "en"},
    {"value": "Mi título", "lang": "es"}
  ]
}
```

**Which is correct?** → **AMBIGUOUS!** 😰

---

## The Synchronization Challenge

### Why MariaDB + GraphDB Makes PATCH Dangerous

```
User PATCH Request: "Update French title"
         ↓
    Symfony API
         ↓
    ┌────┴────┐
    ↓         ↓
MariaDB    GraphDB

Question: How to ensure BOTH databases interpret "update" identically?
```

**The Risks**:

1. **Different interpretations**: SQL does surgical update, RDF does total replacement → **OUT OF SYNC** ❌
2. **Transaction failure**: SQL succeeds, GraphDB fails → **INCONSISTENT STATE** ❌
3. **Triple matching**: How to find exact triple to update when multiple values/languages exist? ❌

---

## NAKALA's Solution: Unambiguous Operations

### 1. PUT - Total Replacement

```http
PUT /datas/abc123
{
  "metas": [
    {"propertyUri": "nakala:title", "value": "Nouveau titre", "lang": "fr"}
    // ⚠️ All other titles EXPLICITLY removed
  ]
}
```

**Clear semantics**: Replace ENTIRE metadata array
- ✅ Unambiguous
- ✅ MariaDB and GraphDB interpret identically
- ⚠️ **Dangerous**: Easy to accidentally delete existing data

---

### 2. POST /metadatas - Add Single Metadata

```http
POST /datas/abc123/metadatas
{
  "propertyUri": "nakala:title",
  "value": "Nouveau titre",
  "lang": "fr",
  "typeUri": "xsd:string"
}
```

**Clear semantics**: Add ONE new metadata entry
- ✅ Safe - doesn't touch existing data
- ✅ Atomic operation in both databases
- ✅ No ambiguity

**What happens**:
```
MariaDB: INSERT INTO metadata (...)
GraphDB: INSERT { nakala:abc123 nakala:title "Nouveau titre"@fr }
```

---

### 3. DELETE /metadatas - Remove Specific Metadata

```http
DELETE /metadatas/{metadata-id}
```

**Clear semantics**: Remove EXACTLY this metadata entry by unique ID
- ✅ Precise targeting (uses database ID, not ambiguous matching)
- ✅ Atomic operation in both databases
- ✅ No risk of deleting wrong entry

**What happens**:
```
MariaDB: DELETE FROM metadata WHERE id = {metadata-id}
GraphDB: DELETE { nakala:abc123 nakala:title "Old value"@fr }
```

---

### 4. PATCH /relations - Works Because Relations Are Simple!

```http
PATCH /datas/abc123/relations
{
  "relation": "10.34847/nkl.xyz789",
  "comment": "Updated comment"
}
```

**Why PATCH works here**:
- Relations = simple string comments (no structure, no languages, no multiple values)
- Unambiguous target (relation ID uniquely identifies the comment)
- No synchronization complexity

**What happens**:
```
MariaDB: UPDATE relations SET comment = 'Updated comment' WHERE ...
GraphDB: DELETE + INSERT single triple (simple)
```

---

## Teaching Exercise

### Interactive Question

You have this metadata:
```json
{
  "creator": [
    {"givenname": "Marie", "surname": "Curie"},
    {"givenname": "Pierre", "surname": "Curie"}
  ]
}
```

You want to change Marie's surname to "Curie-Sklodowska".

**If PATCH were allowed, what could go wrong?**

<details>
<summary>Click to see answer</summary>

**Problems**:
1. How to target exactly Marie's entry? (Both have surname "Curie")
2. If GraphDB deletes ALL creators with surname="Curie", Pierre is lost!
3. If it merges, you might end up with "Marie Curie-Sklodowska" AND "Marie Curie"

**NAKALA's approach**:
```python
# Step 1: Add corrected creator
POST /metadatas {
  "propertyUri": "nakala:creator",
  "value": {"givenname": "Marie", "surname": "Curie-Sklodowska"}
}

# Step 2: Remove old creator entry
DELETE /metadatas/{marie-old-id}

# Pierre untouched ✅
# No ambiguity ✅
```
</details>

---

## Key Takeaways

### 1. Why No PATCH for Metadata?

NAKALA uses **two synchronized databases**:
- **MariaDB (SQL)**: Fast relational queries
- **GraphDB (RDF)**: Semantic search with triples

**RDF triples are atomic** → Can't partially update, only DELETE + INSERT.

With multilingual/multivalued metadata, PATCH becomes **ambiguous**.

---

### 2. Why PATCH Works for Relations?

Relations are **simple text comments** (no structure, no languages, no multiple values).

**Unambiguous** → Easy to update in both databases.

---

### 3. Recommended Pattern 🏆

```python
# ✅ GOOD: Atomic operations
# Step 1: Add new metadata
POST /metadatas {
  "propertyUri": "nakala:title",
  "value": "Nouveau",
  "lang": "fr"
}

# Step 2: Remove old metadata
DELETE /metadatas/{old-metadata-id}

# ✅ Clear, safe, atomic
# ✅ Both databases stay synchronized
```

---

## Visual Summary

```
User Intent: "Change French title only"
              ↓
         [PATCH Request]
              ↓
     ┌────────┴─────────────┐
     ↓                      ↓
 MariaDB                GraphDB
     ↓                      ↓
 "Update                "Delete old triple
  1 specific              + Insert new triple"
  row"                        ↓
     ↓                   "But WHICH triple?"
 CLEAR                   ↓
                     AMBIGUOUS ❌
                         ↓
                  Potential mismatch
                         ↓
                  DATA CORRUPTION 🔥
```

**NAKALA's Solution**: Only allow **unambiguous operations** (POST/DELETE/PUT) to prevent corruption.

---

## For Curious Learners

### Further Reading

- **RDF/SPARQL**: Learn about semantic web technologies
- **Database Synchronization**: Study dual-write patterns
- **REST API Design**: Understand trade-offs in API design

### Questions for Discussion

1. Can you think of scenarios where PATCH would be safe?
2. Why does the dual database architecture add complexity?
3. How would you explain this to a non-technical researcher?

---

**See Also**:
- [PATCH vs PUT](patch_vs_put.md) - Detailed technical explanation
- [REST API Basics](rest_api_basics.md) - HTTP methods explained
- [Workflow](workflow.md) - Complete batch operations workflow
