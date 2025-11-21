# PATCH vs PUT Explained

Why NAKALA uses PUT and POST/DELETE instead of PATCH for metadata updates.

---

## The Question

"Why can't I use PATCH to update just one field in my dataset?"

**Short Answer**: NAKALA's architecture prioritizes data consistency and safety over REST purity.

---

## Where PATCH Works in NAKALA

### ✅ PATCH IS Available For:

```
PATCH /datas/{identifier}/relations    → Update relation comments
```

**Why it works**: Relation comments are simple strings with no complex validation.

### ❌ PATCH is NOT Available For:

```
PATCH /datas/{identifier}              → Returns 405 Method Not Allowed
PATCH /collections/{identifier}        → Returns 405 Method Not Allowed
```

**Why it doesn't work**: Complex metadata with mandatory fields and validation rules.

---

## The Problem with PATCH for Metadata

### Scenario: Multilingual Metadata

**Current state**:
```json
{
  "title": [
    {"value": "My Title", "lang": "en"},
    {"value": "Mon Titre", "lang": "fr"},
    {"value": "Mi Título", "lang": "es"}
  ]
}
```

**User sends PATCH**:
```json
{
  "title": {"value": "New Title", "lang": "en"}
}
```

### ❓ What Should Happen?

**Option 1**: Replace ONLY English title (surgical update)
```json
{
  "title": [
    {"value": "New Title", "lang": "en"},     // ✅ Updated
    {"value": "Mon Titre", "lang": "fr"},     // ✅ Preserved
    {"value": "Mi Título", "lang": "es"}      // ✅ Preserved
  ]
}
```

**Option 2**: Replace ALL titles (total replacement)
```json
{
  "title": [
    {"value": "New Title", "lang": "en"}      // ✅ Updated
    // ❌ French and Spanish lost!
  ]
}
```

**Option 3**: Add new title (merge/append)
```json
{
  "title": [
    {"value": "My Title", "lang": "en"},      // ❌ Duplicate!
    {"value": "New Title", "lang": "en"},     // ✅ New
    {"value": "Mon Titre", "lang": "fr"},
    {"value": "Mi Título", "lang": "es"}
  ]
}
```

**Which is correct?** → **AMBIGUOUS!** 😰

---

## Why This Matters: The 5 Mandatory Fields

Every published dataset requires:
1. title
2. type
3. creator
4. created
5. license

### The Validation Problem

**If PATCH were allowed**:
```json
PATCH /datas/{id}
{
  "metas": [
    {"propertyUri": "nakala:title", "value": "New Title"}
  ]
}
```

**Questions**:
- ❓ What happens to the other 4 mandatory fields?
- ❓ If they're deleted → dataset becomes invalid!
- ❓ If they're kept → we need to query them first (expensive)
- ❓ If we merge → complex logic with many edge cases

---

## NAKALA's Solution: Clear, Unambiguous Operations

### 1. PUT - Total Replacement (Clear but Dangerous)

```http
PUT /datas/abc123
{
  "metas": [
    {"propertyUri": "nakala:title", "value": "New Title"}
    // ⚠️ All other fields EXPLICITLY removed
  ]
}
```

**Semantics**: Replace ENTIRE metadata array
- ✅ Unambiguous
- ✅ Clear what happens
- ⚠️ **Dangerous**: Easy to accidentally delete existing data

---

### 2. POST /metadatas - Add Single Metadata (Recommended)

```http
POST /datas/abc123/metadatas
{
  "propertyUri": "nakala:title",
  "value": "New Title",
  "lang": "en",
  "typeUri": "xsd:string"
}
```

**Semantics**: Add ONE new metadata entry
- ✅ Safe - doesn't touch existing data
- ✅ Atomic operation
- ✅ No ambiguity

---

### 3. DELETE /metadatas - Remove Specific Metadata

```http
DELETE /metadatas/{metadata-id}
```

**Semantics**: Remove EXACTLY this metadata entry by unique ID
- ✅ Precise targeting
- ✅ Atomic operation
- ✅ No risk of deleting wrong entry

---

## Comparison Table

| Operation | Semantics | Safe? | Use Case |
|-----------|-----------|-------|----------|
| **PUT** | Replace all | ⚠️ Risky | Complete rewrites |
| **POST /metadatas** | Add one | ✅ Safe | Adding metadata |
| **DELETE /metadatas** | Remove one | ✅ Safe | Removing metadata |
| **PATCH** (not available) | Update one | ❌ Ambiguous | N/A |
| **PATCH /relations** | Update comment | ✅ Safe | Relation comments only |

---

## Recommended Pattern 🏆

### To Update Metadata:

```python
# ✅ GOOD: Atomic operations
# Step 1: Add new metadata
POST /metadatas {
  "propertyUri": "nakala:title",
  "value": "New Title",
  "lang": "en"
}

# Step 2: Remove old metadata
DELETE /metadatas/{old-metadata-id}

# ✅ Clear, safe, atomic
# ✅ Both databases stay synchronized
```

### To Avoid:

```python
# ❌ BAD: Total replacement with PUT
PUT /datas/{id} {"metas": [...]}  # Risk of losing data if incomplete
```

---

## Why PATCH Works for Relations

Relations are **simple text comments** (no structure, no languages, no multiple values).

```json
{
  "relation": "10.34847/nkl.xyz789",
  "comment": "This is a related dataset"
}
```

**PATCH is safe here because**:
- ✅ Simple string - no complex validation
- ✅ Comments are optional - no strict requirements
- ✅ Updating one comment doesn't affect others
- ✅ No mandatory fields to worry about

**Example**:
```http
PATCH /datas/10.34847/nkl.abc123/relations
{
  "relation": "10.34847/nkl.xyz789",
  "comment": "Updated comment text"
}
```

---

## The Real Reason: Business Logic Safety

### NAKALA's Design Decision

**Prioritize**: Data consistency over REST purity

**Why**:
1. **5 mandatory fields** for published data must always be present
2. **Field interdependencies** (type field affects validation)
3. **Multiple values** (same property can have multiple values/languages)
4. **Merge semantics unclear** (replace, append, or merge?)
5. **Database synchronization** (MariaDB + GraphDB must stay in sync)

### The Philosophy

```
┌──────────────────────────────────────────────────────────┐
│  NAKALA's HTTP Method Philosophy                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  "We prioritize data consistency and semantic clarity   │
│   over strict REST ideology."                           │
│                                                          │
│  • PUT for complete replacement (clear semantics)       │
│  • POST/DELETE for incremental changes (explicit)       │
│  • PATCH only for simple, independent fields            │
│                                                          │
│  This design ensures:                                   │
│  ✅ No invalid intermediate states                      │
│  ✅ Clear user expectations                             │
│  ✅ Reliable database synchronization                   │
│  ✅ Maintainable codebase                               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Practical Advice

### ✅ Do This:

```python
# Get current state
response = requests.get(f"{API_URL}/datas/{dataset_id}", headers=headers)
current_metadata = response.json()["metas"]

# Add new metadata
new_metadata = {
    "propertyUri": "http://nakala.fr/terms#description",
    "value": "New description",
    "lang": "en"
}
requests.post(
    f"{API_URL}/datas/{dataset_id}/metadatas",
    json=new_metadata,
    headers=headers
)

# Remove old metadata (if needed)
requests.delete(
    f"{API_URL}/metadatas/{old_metadata_id}",
    headers=headers
)
```

### ❌ Don't Do This:

```python
# Trying to use PATCH on main resource
requests.patch(
    f"{API_URL}/datas/{dataset_id}",
    json={"metas": [...]},
    headers=headers
)
# → Returns 405 Method Not Allowed
```

---

## Key Takeaways

✅ **PATCH is limited in NAKALA** - only for relation comments  
✅ **Use POST/DELETE /metadatas** for incremental metadata changes  
✅ **PUT replaces everything** - dangerous, use with caution  
✅ **This design prevents data corruption** - prioritizes safety  
✅ **Achieves same goal as PATCH** - just different pattern

---

## Try It in the Workshop

- **Notebook 2**: Uses POST/DELETE /metadatas pattern (see cells 4-7)
- **Observe**: How incremental updates work without PATCH
- **Experiment**: Try adding/removing individual metadata fields

---

**See Also**:
- [REST API Basics](rest_api_basics.md) - HTTP methods explained
- [Database Synchronization](database_sync.md) - Why this architecture exists
- [Quick Reference](quick_reference.md) - API endpoints cheat sheet
