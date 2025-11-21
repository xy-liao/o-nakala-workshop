# CSV Format Guide

**Strict Specification** for the `nakala` Python package's CSV-to-JSON conversion engine.

The `csv_converter.py` engine strictly parses these formats to generate valid NAKALA JSON-LD. Do not deviate from these patterns, or the automatic conversion will fail.

Quick reference for formatting CSV files for NAKALA batch operations.

---

## Core Syntax Rules

### Separators

| Symbol | Purpose | Example |
|--------|---------|---------|
| `:` | Language separator | `en:Title` |
| `;` | Multiple values | `keyword1;keyword2;keyword3` |
| `\|` | Multiple languages | `en:Title\|fr:Titre` |

### Hierarchy

```
|  (pipe)      → Separates languages
;  (semicolon) → Separates multiple values
:  (colon)     → Separates language from content
```

---

## Required Fields

### 1. Title (Multilingual)

```csv
title
"en:My Dataset|fr:Mon jeu de données"
```

### 2. Type (COAR Resource Type URI)

```csv
type
"http://purl.org/coar/resource_type/c_ddb1"
```

Common types:
- Dataset: `http://purl.org/coar/resource_type/c_ddb1`
- Image: `http://purl.org/coar/resource_type/c_c513`
- Text: `http://purl.org/coar/resource_type/c_18cf`
- Software: `http://purl.org/coar/resource_type/c_5ce6`

### 3. Creator (Structured Format)

```csv
creator
"Surname,Given|Surname2,Given2"
```

For multilingual:
```csv
creator
"fr:Dupont,Jean|en:Dupont,Jean"
```

### 4. Created (ISO Date)

```csv
created
"2024"
"2024-01"
"2024-01-15"
```

### 5. License

```csv
license
"CC-BY-4.0"
"CC-BY-NC-4.0"
"CC-BY-SA-4.0"
```

---

## Optional Fields

### Description (Multilingual)

```csv
description
"en:This is a description|fr:Ceci est une description"
```

### Keywords (Multilingual, Multiple Values)

```csv
keywords
"en:keyword1;keyword2;keyword3|fr:mot-clé1;mot-clé2;mot-clé3"
```

### Subject (Multilingual, Multiple Values)

```csv
subject
"en:History;Archaeology|fr:Histoire;Archéologie"
```

---

## File References

### Single File

```csv
files
"files/data/myfile.csv"
```

### Multiple Files

```csv
files
"files/data/file1.csv|files/data/file2.csv"
```

### Directory (All Files)

```csv
files
"files/data/"
```

---

## Collection References

### Single Collection

```csv
collections
"files/data/"
```

### Multiple Collections

```csv
collections
"files/data/|files/images/"
```

---

## Complete Example

```csv
title,creator,created,license,type,description,keywords,files,status
"en:Research Dataset|fr:Jeu de données de recherche","Dupont,Jean","2024","CC-BY-4.0","http://purl.org/coar/resource_type/c_ddb1","en:Survey data from 2024|fr:Données d'enquête de 2024","en:research;data;survey|fr:recherche;données;enquête","files/data/","pending"
```

---

## Common Patterns

### Multilingual Title + Description

```csv
title,description
"en:Title|fr:Titre","en:Description|fr:Description"
```

### Multiple Creators

```csv
creator
"Dupont,Jean|Martin,Marie|Bernard,Pierre"
```

### Multiple Keywords in Multiple Languages

```csv
keywords
"en:keyword1;keyword2;keyword3|fr:mot-clé1;mot-clé2;mot-clé3"
```

---

## Best Practices

### 1. Always Quote Fields with Delimiters

✅ Good:
```csv
"en:Title|fr:Titre"
```

❌ Bad:
```csv
en:Title|fr:Titre
```

### 2. Use Consistent Language Codes

Use ISO 639-1 codes: `en`, `fr`, `de`, `es`, etc.

### 3. Maintain Field Order

Keep the same column order across all rows.

### 4. Validate URIs

Ensure type URIs are complete and valid COAR resource types.

---

## Troubleshooting

### Issue: Pipe character not recognized

**Solution**: Ensure field is quoted:
```csv
"en:Value|fr:Valeur"
```

### Issue: Semicolons breaking keywords

**Solution**: Quote the entire field:
```csv
"en:keyword1;keyword2;keyword3"
```

### Issue: Creator names with commas

**Solution**: Use standard format `"Surname,Given"` - this is correct!

---

## Quick Reference Table

| Field | Required? | Format | Example |
|-------|-----------|--------|---------|
| title | ✅ Yes | `lang:value\|lang:value` | `"en:Title\|fr:Titre"` |
| type | ✅ Yes | COAR URI | `"http://purl.org/coar/resource_type/c_ddb1"` |
| creator | ✅ Yes | `Surname,Given` | `"Dupont,Jean"` |
| created | ✅ Yes | ISO date | `"2024"` or `"2024-01-15"` |
| license | ✅ Yes | License code | `"CC-BY-4.0"` |
| description | No | `lang:value\|lang:value` | `"en:Desc\|fr:Desc"` |
| keywords | No | `lang:val;val\|lang:val` | `"en:key1;key2"` |
| files | No | Path or directory | `"files/data/"` |
| status | No | `pending`/`published` | `"pending"` |

---

**See Also**:
- [Quick Reference](quick_reference.md) - API basics
- [Metadata Fields](metadata_fields.md) - Detailed field explanations
- [Troubleshooting](troubleshooting.md) - Common issues
