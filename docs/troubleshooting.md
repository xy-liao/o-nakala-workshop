# Troubleshooting

Common issues and solutions for NAKALA batch operations.

---

## CSV Format Issues

### Issue: "Invalid CSV format" error

**Symptoms**: Script fails to read CSV file

**Solutions**:
1. Check file encoding is UTF-8
2. Ensure all fields with delimiters are quoted
3. Verify no extra commas at end of rows

**Example Fix**:
```csv
# ❌ Wrong
title,creator
en:Title|fr:Titre,Dupont,Jean

# ✅ Correct
title,creator
"en:Title|fr:Titre","Dupont,Jean"
```

---

### Issue: Multilingual fields not recognized

**Symptoms**: Only first language appears, or pipe character shows literally

**Solution**: Quote the entire field

```csv
# ❌ Wrong
en:Title|fr:Titre

# ✅ Correct
"en:Title|fr:Titre"
```

---

### Issue: Keywords not splitting correctly

**Symptoms**: All keywords appear as single value

**Solution**: Use semicolons and quote the field

```csv
# ❌ Wrong
keyword1,keyword2,keyword3

# ✅ Correct
"keyword1;keyword2;keyword3"
```

---

## API Connection Issues

### Issue: "401 Unauthorized" error

**Symptoms**: All API calls fail with 401

**Solutions**:
1. Check API key is correct
2. Verify API key header: `X-API-KEY`
3. Ensure using test API key for test environment

**Check**:
```python
headers = {
    "X-API-KEY": "aae99aba-476e-4ff2-2886-0aaf1bfa6fd2",  # Test key
    "Content-Type": "application/json"
}
```

---

### Issue: "404 Not Found" error

**Symptoms**: Resource not found

**Solutions**:
1. Verify resource ID is correct
2. Check resource exists (GET request first)
3. Ensure using correct API URL (test vs production)

---

### Issue: "405 Method Not Allowed" error

**Symptoms**: PATCH request fails on `/datas/{id}`

**Explanation**: PATCH is not available for main dataset endpoint

**Solution**: Use POST/DELETE on `/metadatas` sub-resource instead

```python
# ❌ Not available
PATCH /datas/{id}

# ✅ Use instead
POST /datas/{id}/metadatas
DELETE /datas/{id}/metadatas
```

---

## Metadata Validation Issues

### Issue: "Missing mandatory field" error

**Symptoms**: Dataset creation fails with 422 error

**Solution**: Ensure all 5 mandatory fields are present:
- title
- type
- creator
- created
- license

**Check**:
```csv
title,type,creator,created,license
"en:Title","http://purl.org/coar/resource_type/c_ddb1","Dupont,Jean","2024","CC-BY-4.0"
```

---

### Issue: "Invalid type URI" error

**Symptoms**: Type field rejected

**Solution**: Use full COAR URI, not short code

```csv
# ❌ Wrong
type
"dataset"

# ✅ Correct
type
"http://purl.org/coar/resource_type/c_ddb1"
```

---

### Issue: "Invalid date format" error

**Symptoms**: Created date rejected

**Solution**: Use ISO 8601 format

```csv
# ✅ All valid
"2024"
"2024-01"
"2024-01-15"

# ❌ Invalid
"01/15/2024"
"15-01-2024"
```

---

## File Upload Issues

### Issue: "File not found" error

**Symptoms**: File upload fails

**Solutions**:
1. Check file path is correct (relative to script location)
2. Verify file exists
3. Ensure file permissions allow reading

**Check**:
```python
from pathlib import Path
file_path = Path("files/data/myfile.csv")
print(f"Exists: {file_path.exists()}")
print(f"Absolute: {file_path.absolute()}")
```

---

### Issue: "File too large" error

**Symptoms**: Upload fails for large files

**Solution**: NAKALA has file size limits. Split large files or contact support.

---

## Deletion Issues

### Issue: "Cannot delete published dataset" error

**Symptoms**: DELETE request fails with error

**Explanation**: Published datasets cannot be deleted via API (data preservation)

**Solution**: Contact Huma-Num staff for manual deletion

**Check status first**:
```python
response = requests.get(f"{API_URL}/datas/{dataset_id}", headers=headers)
status = response.json().get("status")
print(f"Status: {status}")  # Only "pending" can be deleted
```

---

### Issue: Collection deletion fails

**Symptoms**: DELETE /collections/{id} returns error

**Solutions**:
1. Verify you're the collection owner
2. Check collection exists
3. Note: Deleting collection doesn't delete contained datasets

---

## Notebook-Specific Issues

### Issue: "Module not found" error

**Symptoms**: `from nakala.config import ...` fails

**Solution**: Ensure `sys.path` includes parent directory

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
```

---

### Issue: Kernel selection confusion

**Symptoms**: Jupyter asks which kernel to use

**Solution**: 
- If using venv: Select "Python 3" or "Python [venv]"
- If using Conda: Select "Python [conda env:base]"

---

### Issue: Generated CSVs not found

**Symptoms**: Notebook 2 can't find modification CSVs

**Solution**: Run Notebook 1 completely first - it generates the CSVs

**Check**:
```python
from pathlib import Path
data_path = Path("../data")
print("Generated CSVs:")
for csv_file in data_path.glob("*.csv"):
    print(f"  - {csv_file.name}")
```

---

## Common Error Messages

### "propertyUri is required"

**Cause**: Missing or invalid metadata property URI

**Fix**: Ensure all metadata objects have `propertyUri` field

---

### "value cannot be empty"

**Cause**: Empty metadata value

**Fix**: Provide non-empty value or remove the metadata field

---

### "Invalid language code"

**Cause**: Non-standard language code

**Fix**: Use ISO 639-1 codes (en, fr, de, es, etc.)

---

## Performance Issues

### Issue: Slow CSV processing

**Symptoms**: Large CSV files take long to process

**Solutions**:
1. Process in batches
2. Remove unnecessary columns
3. Optimize file I/O

---

### Issue: API rate limiting

**Symptoms**: Requests start failing after many operations

**Solution**: Add delays between requests

```python
import time
time.sleep(1)  # Wait 1 second between requests
```

---

## Getting Help

### Check Logs

Look for detailed error messages in:
- Notebook output cells
- Console/terminal output
- Log files (if enabled)

### Verify Data

Before reporting issues:
1. Check CSV format is correct
2. Verify all mandatory fields present
3. Test with minimal example

### Resources

- [CSV Format Guide](csv_format_guide.md) - Correct CSV formatting
- [Quick Reference](quick_reference.md) - API basics
- [Workflow](workflow.md) - Expected process flow

---

## Quick Diagnostic Checklist

When something fails, check:

- [ ] CSV file is UTF-8 encoded
- [ ] All fields with delimiters are quoted
- [ ] All 5 mandatory fields are present
- [ ] Type field uses full COAR URI
- [ ] Date is in ISO format
- [ ] API key is correct
- [ ] Using correct API URL (test vs production)
- [ ] Resource exists (for GET/PATCH/DELETE)
- [ ] Resource status is "pending" (for DELETE)
- [ ] File paths are correct
- [ ] Python path includes nakala package

---

**Still stuck?** Review the [workflow documentation](workflow.md) to ensure you're following the correct process.
