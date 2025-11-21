# Metadata Fields Explained

Deep dive into the 5 mandatory NAKALA metadata fields.

---

## Overview

Every published NAKALA dataset requires exactly **5 mandatory fields**:

1. **title** - What the dataset is called
2. **type** - What kind of resource it is
3. **creator** - Who created it
4. **created** - When it was created
5. **license** - How it can be used

---

## 1. Title

### Purpose
The name/title of your dataset, visible to all users.

### Format
Multilingual string with language codes.

### Examples

**Single language**:
```csv
"en:Research Data from 2024 Survey"
```

**Multiple languages**:
```csv
"en:Research Data from 2024 Survey|fr:Données de recherche de l'enquête 2024"
```

### Best Practices
- ✅ Be descriptive and specific
- ✅ Include key information (topic, date, type)
- ✅ Provide translations for international visibility
- ❌ Don't use generic titles like "Data" or "File"
- ❌ Don't include special characters that break CSV

### Common Patterns
```csv
# Academic research
"en:Climate Change Survey Data 2024|fr:Données d'enquête sur le changement climatique 2024"

# Digital humanities
"en:Medieval Manuscript Collection|fr:Collection de manuscrits médiévaux"

# Archive digitization
"en:Historical Photographs 1920-1950|fr:Photographies historiques 1920-1950"
```

---

## 2. Type

### Purpose
Categorizes the resource using standardized COAR vocabulary.

### Format
Full URI from COAR Resource Type vocabulary.

### Common Types

| Resource Type | COAR URI |
|---------------|----------|
| **Dataset** | `http://purl.org/coar/resource_type/c_ddb1` |
| **Image** | `http://purl.org/coar/resource_type/c_c513` |
| **Text** | `http://purl.org/coar/resource_type/c_18cf` |
| **Software** | `http://purl.org/coar/resource_type/c_5ce6` |
| **Video** | `http://purl.org/coar/resource_type/c_12ce` |
| **Audio** | `http://purl.org/coar/resource_type/c_18cc` |
| **Interactive Resource** | `http://purl.org/coar/resource_type/c_e9a0` |
| **Collection** | `http://purl.org/coar/resource_type/c_collection` |

### Best Practices
- ✅ Use the full URI, not abbreviations
- ✅ Choose the most specific type available
- ✅ Verify URI is from official COAR vocabulary
- ❌ Don't use custom or shortened URIs
- ❌ Don't use generic "resource" type unless necessary

### Example
```csv
type
"http://purl.org/coar/resource_type/c_ddb1"
```

---

## 3. Creator

### Purpose
Identifies who created or is responsible for the resource.

### Format
Structured as `Surname,Given` (note the comma!).

### Examples

**Single creator**:
```csv
"Dupont,Jean"
```

**Multiple creators**:
```csv
"Dupont,Jean|Martin,Marie|Bernard,Pierre"
```

**Multilingual (if name varies by language)**:
```csv
"fr:Dupont,Jean|en:Dupont,John"
```

### Best Practices
- ✅ Use format: `Surname,Given` (comma-separated)
- ✅ List all significant contributors
- ✅ Maintain consistent name formatting
- ❌ Don't use "First Last" format
- ❌ Don't include titles (Dr., Prof., etc.)
- ❌ Don't use organizational names without structure

### Special Cases

**Organization as creator**:
```csv
"Research Institute,Department of History"
```

**Single-name creators**:
```csv
"Plato,"
```

**Compound surnames**:
```csv
"García-López,María"
```

---

## 4. Created

### Purpose
When the resource was created or published.

### Format
ISO 8601 date format (YYYY, YYYY-MM, or YYYY-MM-DD).

### Examples

**Year only**:
```csv
"2024"
```

**Year and month**:
```csv
"2024-01"
```

**Full date**:
```csv
"2024-01-15"
```

### Best Practices
- ✅ Use ISO 8601 format (YYYY-MM-DD)
- ✅ Be as specific as possible
- ✅ Use creation date, not upload date
- ❌ Don't use formats like "01/15/2024" or "15-01-2024"
- ❌ Don't use relative dates like "last year"

### Common Scenarios

**Historical data**:
```csv
"1920"  # Only year known
```

**Recent research**:
```csv
"2024-03-15"  # Exact date known
```

**Ongoing project**:
```csv
"2024"  # Use start year
```

---

## 5. License

### Purpose
Defines how others can use your data.

### Format
License identifier (preferably Creative Commons).

### Common Licenses

| License | Code | Allows |
|---------|------|--------|
| **CC-BY-4.0** | `CC-BY-4.0` | Use, share, adapt (with attribution) |
| **CC-BY-NC-4.0** | `CC-BY-NC-4.0` | Non-commercial use only |
| **CC-BY-SA-4.0** | `CC-BY-SA-4.0` | Share-alike required |
| **CC-BY-ND-4.0** | `CC-BY-ND-4.0` | No derivatives allowed |
| **CC0-1.0** | `CC0-1.0` | Public domain dedication |

### Best Practices
- ✅ Use standard Creative Commons licenses
- ✅ Choose most open license possible
- ✅ Consider CC-BY-4.0 as default for research data
- ❌ Don't use custom or proprietary licenses
- ❌ Don't leave license unspecified

### Choosing a License

**For maximum reuse** (recommended for research):
```csv
"CC-BY-4.0"
```

**For non-commercial only**:
```csv
"CC-BY-NC-4.0"
```

**For public domain**:
```csv
"CC0-1.0"
```

---

## Complete Example

All 5 mandatory fields together:

```csv
title,type,creator,created,license
"en:Climate Survey Data 2024|fr:Données d'enquête climatique 2024","http://purl.org/coar/resource_type/c_ddb1","Dupont,Jean|Martin,Marie","2024-03-15","CC-BY-4.0"
```

---

## Validation Checklist

Before submitting, verify:

- [ ] **Title**: Descriptive, multilingual if possible
- [ ] **Type**: Full COAR URI (starts with `http://purl.org/coar/`)
- [ ] **Creator**: Format is `Surname,Given`
- [ ] **Created**: ISO 8601 format (YYYY-MM-DD)
- [ ] **License**: Standard license code (e.g., CC-BY-4.0)
- [ ] All fields are quoted if they contain delimiters
- [ ] No empty values

---

## Common Mistakes

### ❌ Wrong

```csv
title,type,creator,created,license
My Dataset,dataset,John Dupont,01/15/2024,Creative Commons
```

**Problems**:
- Title not multilingual
- Type not full URI
- Creator wrong format
- Date wrong format
- License not standard code

### ✅ Correct

```csv
title,type,creator,created,license
"en:My Dataset","http://purl.org/coar/resource_type/c_ddb1","Dupont,John","2024-01-15","CC-BY-4.0"
```

---

## Field Dependencies

### Status-Dependent Requirements

| Status | Mandatory Fields Required? |
|--------|---------------------------|
| `pending` | No (can be incomplete) |
| `published` | **Yes** (all 5 required) |

**Note**: You can create datasets with status `pending` without all mandatory fields, but they cannot be published until all 5 fields are present.

---

## Optional but Recommended Fields

While not mandatory, these fields enhance discoverability:

- **description** - Detailed explanation of the dataset
- **keywords** - Search terms
- **subject** - Topic classification
- **publisher** - Publishing organization
- **contributor** - Additional contributors

---

## See Also

- [CSV Format Guide](csv_format_guide.md) - How to format these fields in CSV
- [Quick Reference](quick_reference.md) - Quick lookup table
- [Troubleshooting](troubleshooting.md) - Common field validation errors
