# REST API Basics

Understanding HTTP methods, URLs, and requests for NAKALA API.

---

## 🍽️ The Restaurant Analogy

Think of a REST API like a restaurant:

```
REST API           =  Restaurant
URL                =  Table number
HTTP Method        =  What you want to do
Request Body       =  Your order details
Response           =  What you get back
```

### Examples

```
GET /table/5       =  "Show me what's on table 5"
POST /table/5      =  "Place this order at table 5"
PATCH /table/5     =  "Change just the drink"
PUT /table/5       =  "Replace EVERYTHING on the table"
DELETE /table/5    =  "Clear everything from table 5"
```

---

## HTTP Methods Explained

### GET - Reading (Safe, No Changes)

**Restaurant**: "Waiter, show me what's on Table 5"

**NAKALA**:
```
GET /datas/10.34847/nkl.abc123

Response: Full dataset metadata
Result: Nothing changed, just retrieved information
```

**Use when**:
- Checking if dataset exists
- Reading current metadata
- Viewing file list
- **Always safe** - never modifies data

---

### POST - Creating New

**Restaurant**: "Waiter, I'd like to order for Table 5" (new table)

**NAKALA**:
```
POST /datas

Body: Complete dataset metadata + files

Response: 201 Created
{ "identifier": "10.34847/nkl.abc123" }

Result: New dataset created
```

**Use when**:
- Creating NEW dataset
- Creating NEW collection
- Uploading files
- Adding metadata incrementally

---

### PATCH - Partial Update (Surgical Change)

**Restaurant**: "Keep everything but change my drink to wine"

**Generic REST**:
```
PATCH /datas/10.34847/nkl.abc123
Body: { "title": "Updated Title" }

Result: ONLY title changed, everything else preserved
```

**⚠️ NAKALA Limitation**:
- PATCH is **NOT available** for `/datas/{id}` (returns 405)
- PATCH **IS available** for `/datas/{id}/relations` only

**NAKALA Alternative**:
```
# Use POST/DELETE on /metadatas sub-resource
POST /datas/{id}/metadatas
DELETE /datas/{id}/metadatas
```

---

### PUT - Complete Replacement (Dangerous!)

**Restaurant**: "Clear my entire table and bring me ONLY wine"

**NAKALA**:
```
PUT /datas/10.34847/nkl.abc123
Body: { "metas": [{"propertyUri": "...", "value": "New Title"}] }

Result: Dataset now has ONLY title
        All other fields REMOVED!
        → Dataset becomes INVALID (missing mandatory fields)
```

**⚠️ Warning**: PUT replaces EVERYTHING. Forget a field = it's deleted!

**Use when**:
- Completely rebuilding metadata from scratch
- You have ALL mandatory fields included
- **Rarely used** - prefer POST/DELETE /metadatas

---

### DELETE - Removing (Irreversible)

**Restaurant**: "Clear everything from Table 5, I'm done"

**NAKALA**:
```
DELETE /datas/10.34847/nkl.abc123

Response: 204 No Content

Result: Dataset permanently removed
```

**⚠️ Restrictions**:
- Only works if status = "pending"
- Cannot delete published datasets (data preservation)
- Irreversible!

---

## HTTP Methods Summary Table

| Method | Restaurant Action | Safe? | Use Case |
|--------|------------------|-------|----------|
| **GET** | "Show me what's there" | ✅ Safe | Read data |
| **POST** | "Place this order" (new) | ✅ Safe | Create new |
| **PATCH** | "Change just the drink" | ✅ Safe | Partial update (limited in NAKALA) |
| **PUT** | "Replace EVERYTHING" | ⚠️ Dangerous | Full replacement |
| **DELETE** | "Clear the table" | ⚠️ Irreversible | Remove resource |

---

## 🔑 PATCH vs PUT: The Critical Difference

### Scenario: You have a 3-course meal

- Appetizer: Salad
- Main: Steak
- Dessert: Ice cream
- Drink: Water

### Using PATCH (Partial Update) ✅

```
Request: PATCH /table/5
Body: { "drink": "wine" }

Result:
✓ Appetizer: Salad (unchanged)
✓ Main: Steak (unchanged)
✓ Dessert: Ice cream (unchanged)
✓ Drink: Wine (changed)
```

**Only what you specified changed!**

### Using PUT (Full Replacement) ⚠️

```
Request: PUT /table/5
Body: { "drink": "wine" }

Result:
✗ Appetizer: GONE
✗ Main: GONE
✗ Dessert: GONE
✓ Drink: Wine (only thing left)
```

**You just lost your $50 steak because you forgot to mention it!**

---

## URL Structure

### Anatomy of a NAKALA API URL

```
https://apitest.nakala.fr/datas/10.34847/nkl.863cxt5l
│      │        │         │     │
│      │        │         │     └─ Resource ID
│      │        │         └─────── Resource Type (datas/collections)
│      │        └───────────────── API Base Path
│      └────────────────────────── Domain (test environment)
└───────────────────────────────── Protocol (HTTPS)
```

---

## NAKALA API Endpoints

### Datasets

```
POST   /datas              → Create dataset
GET    /datas/{id}         → Get dataset
PUT    /datas/{id}         → Replace metadata (dangerous)
DELETE /datas/{id}         → Delete dataset (pending only)
```

### Collections

```
POST   /collections        → Create collection
GET    /collections/{id}   → Get collection
PATCH  /collections/{id}   → Update metadata
DELETE /collections/{id}   → Delete collection
```

### Files

```
POST   /datas/uploads      → Upload file
GET    /data/{id}/{sha1}   → Download file
```

### Metadata (Sub-resource)

```
POST   /datas/{id}/metadatas    → Add metadata
DELETE /datas/{id}/metadatas    → Remove metadata
```

---

## Complete Request Example

### HTTP Request Anatomy

```
PATCH /datas/10.34847/nkl.863cxt5l HTTP/1.1
Host: apitest.nakala.fr
Content-Type: application/json
X-API-KEY: aae99aba-476e-4ff2-2886-0aaf1bfa6fd2

{
  "metas": [
    {
      "value": "Updated Title",
      "propertyUri": "http://nakala.fr/terms#title"
    }
  ]
}
```

**Breaking it down**:
- **Request Line**: PATCH /datas/... (method + URL)
- **Headers**: Host, Content-Type, X-API-KEY
- **Body**: JSON payload (what to update)

---

## Python Example

```python
import requests

# URL = Resource Location
url = "https://apitest.nakala.fr/datas/10.34847/nkl.abc123"

# Authentication
headers = {
    "X-API-KEY": "aae99aba-476e-4ff2-2886-0aaf1bfa6fd2",
    "Content-Type": "application/json"
}

# Action 1: GET - Read the dataset
response = requests.get(url, headers=headers)
print(response.json())  # Shows current metadata

# Action 2: POST - Add metadata
metadata_url = f"{url}/metadatas"
new_metadata = {
    "propertyUri": "http://nakala.fr/terms#description",
    "value": "New description",
    "lang": "en"
}
response = requests.post(metadata_url, json=new_metadata, headers=headers)
print(f"Added metadata: {response.status_code}")

# Action 3: DELETE - Remove dataset (if pending)
response = requests.delete(url, headers=headers)
print(f"Deleted: {response.status_code}")
```

---

## When to Use Each Method in NAKALA

### ✅ Use GET When:
- Checking if dataset exists
- Reading current metadata
- Viewing file list
- **Never modifies data** (always safe)

### ✅ Use POST When:
- Creating NEW dataset
- Creating NEW collection
- Uploading files
- **Adding metadata incrementally** (POST /metadatas)

### ✅ Use PATCH When:
- **Only for /datas/{id}/relations** (update relation comments)
- **NOT available for /datas/{id}** (returns 405)
- **For metadata updates, use POST/DELETE /metadatas instead**

### ✅ Use DELETE When:
- **Removing specific metadata** (DELETE /metadatas)
- Removing pending datasets
- **Cannot delete published datasets**

### ⚠️ Use PUT When:
- Completely rebuilding metadata from scratch
- You have ALL mandatory fields included
- **Dangerous** - prefer POST/DELETE /metadatas

---

## Common Workflows

### 1. Create Dataset

```
1. Upload files (POST /datas/uploads)
2. Create dataset (POST /datas)
3. Verify creation (GET /datas/{id})
```

### 2. Modify Metadata

```
1. Get current metadata (GET /datas/{id})
2. Add new metadata (POST /datas/{id}/metadatas)
3. Remove old metadata (DELETE /datas/{id}/metadatas)
4. Verify changes (GET /datas/{id})
```

### 3. Delete Dataset

```
1. Check status (GET /datas/{id})
2. Delete if pending (DELETE /datas/{id})
3. Confirm deletion
```

---

## Error Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 204 | No Content | Success (no response body) |
| 400 | Bad Request | Invalid data |
| 401 | Unauthorized | Invalid API key |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method (e.g., PATCH on /datas/{id}) |
| 422 | Unprocessable Entity | Validation error (missing mandatory fields) |

---

## Key Takeaways

✅ **GET is always safe** - use it to check before modifying  
✅ **POST creates new** - use for datasets, collections, metadata  
✅ **PATCH is limited in NAKALA** - use POST/DELETE /metadatas instead  
✅ **PUT is dangerous** - replaces everything, easy to lose data  
✅ **DELETE is irreversible** - only works on pending datasets

---

## Try It in the Workshop

- **Notebook 1**: Uses POST to create datasets (see cells 5-8)
- **Notebook 2**: Uses GET then POST/DELETE for modifications (see cells 3-6)
- **Notebook 3**: Uses DELETE to remove resources (see cells 4-7)

---

**See Also**:
- [PATCH vs PUT](patch_vs_put.md) - Why PATCH is limited in NAKALA
- [Quick Reference](quick_reference.md) - API endpoints cheat sheet
- [Workflow](workflow.md) - Complete batch operations workflow
