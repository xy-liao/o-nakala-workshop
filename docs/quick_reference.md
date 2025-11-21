# Quick Reference

Essential NAKALA API information for batch operations.

---

## 5 Mandatory Fields

Every published dataset **MUST** have these fields:

| Field | Format | Example |
|-------|--------|---------|
| **title** | Multilingual string | `"en:My Dataset\|fr:Mon jeu de données"` |
| **type** | COAR resource type URI | `"http://purl.org/coar/resource_type/c_ddb1"` |
| **creator** | Structured name | `"Surname,Given"` |
| **created** | ISO date | `"2024"` or `"2024-01-15"` |
| **license** | License identifier | `"CC-BY-4.0"` |

---

## Common Resource Types

| Type | COAR URI |
|------|----------|
| Dataset | `http://purl.org/coar/resource_type/c_ddb1` |
| Image | `http://purl.org/coar/resource_type/c_c513` |
| Text | `http://purl.org/coar/resource_type/c_18cf` |
| Software | `http://purl.org/coar/resource_type/c_5ce6` |
| Video | `http://purl.org/coar/resource_type/c_12ce` |
| Audio | `http://purl.org/coar/resource_type/c_18cc` |

---

## Common Licenses

| License | Code |
|---------|------|
| Creative Commons Attribution 4.0 | `CC-BY-4.0` |
| CC Attribution-NonCommercial 4.0 | `CC-BY-NC-4.0` |
| CC Attribution-ShareAlike 4.0 | `CC-BY-SA-4.0` |
| CC Attribution-NoDerivatives 4.0 | `CC-BY-ND-4.0` |
| Public Domain | `CC0-1.0` |

---

## HTTP Methods

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Retrieve resource | `GET /datas/{id}` |
| POST | Create resource | `POST /datas` |
| PUT | Full replacement | `PUT /datas/{id}` |
| DELETE | Remove resource | `DELETE /datas/{id}` |

**Note**: PATCH is **only** available for `/datas/{id}/relations` (not for main dataset/collection endpoints). Use `POST/DELETE /metadatas` for incremental metadata updates.

---

## API Endpoints

### Datasets

```
POST   /datas              → Create dataset
GET    /datas/{id}         → Get dataset
PUT    /datas/{id}         → Replace metadata (dangerous!)
DELETE /datas/{id}         → Delete dataset (pending only)
```

### Metadata (Sub-resources - Recommended Pattern)

```
POST   /datas/{id}/metadatas   → Add metadata incrementally
DELETE /datas/{id}/metadatas   → Remove specific metadata
```

### Relations (PATCH only works here)

```
PATCH  /datas/{id}/relations   → Update relation comments
```

### Collections

```
POST   /collections        → Create collection
GET    /collections/{id}   → Get collection
PUT    /collections/{id}   → Replace metadata
DELETE /collections/{id}   → Delete collection
```

### Files

```
POST   /datas/uploads      → Upload file
GET    /data/{id}/{sha1}   → Download file
```

---

## Status Values

| Status | Meaning | Can Delete? |
|--------|---------|-------------|
| `pending` | Draft, not published | ✅ Yes |
| `published` | Public, has DOI | ❌ No (contact Huma-Num) |
| `private` | Private collection | ✅ Yes |
| `public` | Public collection | ✅ Yes |

---

## Multilingual Format

### Single Language

```csv
"en:My Title"
```

### Multiple Languages

```csv
"en:My Title|fr:Mon Titre|de:Mein Titel"
```

### Multiple Values, Multiple Languages

```csv
"en:keyword1;keyword2;keyword3|fr:mot-clé1;mot-clé2;mot-clé3"
```

---

## Creator Format

### Single Creator

```csv
"Dupont,Jean"
```

### Multiple Creators

```csv
"Dupont,Jean|Martin,Marie|Bernard,Pierre"
```

### Multilingual Creator

```csv
"fr:Dupont,Jean|en:Dupont,Jean"
```

---

## Date Formats

| Format | Example | Use Case |
|--------|---------|----------|
| Year only | `"2024"` | Publication year |
| Year-Month | `"2024-01"` | Month precision |
| Full date | `"2024-01-15"` | Exact date |

---

## CSV Separators

| Symbol | Purpose | Example |
|--------|---------|---------|
| `:` | Language separator | `en:Value` |
| `;` | Multiple values | `val1;val2;val3` |
| `\|` | Multiple languages/items | `en:Val\|fr:Val` |

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
| 405 | Method Not Allowed | Wrong HTTP method |
| 422 | Unprocessable Entity | Validation error |

---

## Authentication

### API Key Header

```
X-API-KEY: your-api-key-here
```

### Test API

```
URL: https://apitest.nakala.fr
Key: aae99aba-476e-4ff2-2886-0aaf1bfa6fd2
```

---

## Quick Tips

✅ **Always quote CSV fields** with delimiters (`:`, `;`, `|`)  
✅ **Use full COAR URIs** for type field  
✅ **Check status** before deleting (only pending can be deleted)  
✅ **Test on apitest** before production  
✅ **Include all 5 mandatory fields** for published datasets

❌ **Don't use commas** as separators (use `;` instead)  
❌ **Don't delete published datasets** via API  
❌ **Don't forget language codes** in multilingual fields  
❌ **Don't use partial URIs** for type field

---

**See Also**:
- [CSV Format Guide](csv_format_guide.md) - Detailed CSV formatting
- [Metadata Fields](metadata_fields.md) - Field explanations
- [REST API Basics](rest_api_basics.md) - HTTP methods explained
- [Workflow](workflow.md) - Complete batch operations workflow
