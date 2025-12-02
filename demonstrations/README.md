# Live Demonstrations

**For Instructors**: Interactive Python scripts to demonstrate NAKALA API concepts before participants try the notebooks.

---

## Purpose

These demonstration scripts are designed for **instructor-led live coding** during the workshop:

1. **After slides**: Show concrete examples of concepts just taught
2. **Before notebooks**: Let participants see the workflow in action
3. **During Q&A**: Demonstrate specific features or troubleshoot issues

---

## Workshop Flow

```
📊 Slides (Introduction)
    ↓
🎬 Live Demonstrations (You run these scripts)
    ↓
📓 Hands-on Practice (Participants use notebooks)
```

---

## Available Demonstrations

### 1. Complete NAKALA Lifecycle Demo

**File**: `complete_nakala_lifecycle_demo.py`

**Purpose**: Full workflow combining datasets and collections

**Demonstrates**:
- Creating datasets with files
- Creating collections
- Linking datasets to collections
- Complete cleanup

**Duration**: ~15 minutes

**When to use**: As comprehensive overview before hands-on practice

**Run**:
```bash
python demonstrations/complete_nakala_lifecycle_demo.py
```

---

### 2. Dataset Lifecycle Demo

**File**: `dataset_lifecycle_demo.py`

**Purpose**: Complete dataset workflow from creation to deletion

**Demonstrates**:
- Creating a dataset with files
- Retrieving dataset metadata
- Updating metadata
- Deleting a dataset

**Duration**: ~10 minutes

**When to use**: After introducing datasets, before Notebook 1

**Run**:
```bash
python demonstrations/dataset_lifecycle_demo.py
```

---

### 3. Collection Lifecycle Demo

**File**: `collection_lifecycle_demo.py`

**Purpose**: Complete collection workflow

**Demonstrates**:
- Creating a collection
- Adding datasets to collection
- Updating collection metadata
- Removing datasets from collection
- Deleting collection

**Duration**: ~10 minutes

**When to use**: After introducing collections, before Notebook 1

**Run**:
```bash
python demonstrations/collection_lifecycle_demo.py
```

---

### 4. Incremental Metadata Demo

**File**: `incremental_metadata_demo.py`

**Purpose**: Show POST/DELETE pattern for metadata updates

**Demonstrates**:
- Why PATCH is limited in NAKALA
- Using POST /metadatas to add metadata
- Using DELETE /metadatas to remove metadata
- Comparing with PUT (dangerous)

**Duration**: ~15 minutes

**When to use**: Before Notebook 2, to explain modification strategy

**Links to**: [docs/patch_vs_put.md](../docs/patch_vs_put.md)

**Run**:
```bash
python demonstrations/incremental_metadata_demo.py
```

---

### 5. Metadata Modification Comparison

**File**: `metadata_modification_comparison.py`

**Purpose**: Compare different metadata update approaches

**Demonstrates**:
- PUT (full replacement)
- POST/DELETE (incremental)
- When to use each

**Duration**: ~10 minutes

**When to use**: Advanced topic, after Notebook 2

**Links to**: [docs/patch_vs_put.md](../docs/patch_vs_put.md)

**Run**:
```bash
python demonstrations/metadata_modification_comparison.py
```

---

### 6. Rights Management Demo

**File**: `rights_management_demo.py`

**Purpose**: User permissions and access control

**Demonstrates**:
- Granting user rights
- Checking permissions
- Revoking access
- Group management

**Duration**: ~15 minutes

**When to use**: Advanced topic, optional

**Run**:
```bash
python demonstrations/rights_management_demo.py
```

---

## Recommended Workshop Timeline

### Part 1: Introduction (30 min)
- **Slides**: NAKALA overview, API concepts
- **Show**: [Workflow diagram](../docs/workflow.md)

### Part 2: Live Demonstration (30 min)

**Option A - Quick Overview** (Recommended for beginners):
```bash
python demonstrations/complete_nakala_lifecycle_demo.py
```

**Option B - Detailed Walkthrough** (For in-depth training):
```bash
# 1. Show dataset creation
python demonstrations/dataset_lifecycle_demo.py

# 2. Show collection creation
python demonstrations/collection_lifecycle_demo.py

# 3. Explain modification strategy
python demonstrations/incremental_metadata_demo.py
```

### Part 3: Hands-on Practice (60-90 min)
- **Notebook 1**: Participants create datasets/collections
- **Notebook 2**: Participants modify metadata
- **Notebook 3**: Participants clean up

### Part 4: Advanced Topics (Optional, 30 min)
```bash
# Show advanced patterns
python demonstrations/metadata_modification_comparison.py
python demonstrations/rights_management_demo.py
```

---

## Tips for Instructors

### Before the Workshop

1. **Test all scripts** to ensure they work
2. **Review output** to know what to expect
3. **Prepare talking points** for each demonstration
4. **Have backup** in case of API issues

### During Demonstrations

1. **Explain before running**: Tell participants what will happen
2. **Show the code**: Open the script file, highlight key sections
3. **Run and narrate**: Execute and explain the output
4. **Pause for questions**: Stop at key points for Q&A
5. **Link to docs**: Reference relevant documentation

### Common Questions to Prepare For

- "Why can't I use PATCH?" → Show `incremental_metadata_demo.py`
- "What's the difference between PUT and POST?" → Show `metadata_modification_comparison.py`
- "How do I share datasets?" → Show `rights_management_demo.py`
- "What if something goes wrong?" → Reference [docs/troubleshooting.md](../docs/troubleshooting.md)

---

## Script Dependencies

All scripts use the `nakala/` package (already included in this workshop kit):

```python
from nakala import (
    APIClient,
    CSVConverter,
    # ... other modules
)

from nakala.demo_helpers import (
    print_section_header,
    print_success,
    # ... helper functions
)
```

**No additional setup required** - scripts work out of the box!

---

## Quick Reference

| Script | Duration | Best For | Links To |
|--------|----------|----------|----------|
| complete_nakala_lifecycle_demo.py | 15 min | Full overview | All notebooks |
| dataset_lifecycle_demo.py | 10 min | Dataset basics | Notebook 1 |
| collection_lifecycle_demo.py | 10 min | Collection basics | Notebook 1 |
| incremental_metadata_demo.py | 15 min | Modification strategy | Notebook 2, docs/patch_vs_put.md |
| metadata_modification_comparison.py | 10 min | Advanced modifications | Notebook 2 |
| rights_management_demo.py | 15 min | User permissions | Advanced topic |

---

## Troubleshooting

### Script fails with "Module not found"

**Solution 1**: Ensure you're running from the workshop root directory:
```bash
cd /path/to/o-nakala-workshop
python demonstrations/script_name.py
```

**Solution 2** (Alternative): Install the package in editable mode:
```bash
cd /path/to/o-nakala-workshop
pip install -e .
# Now you can run scripts from anywhere
python demonstrations/script_name.py
```

**Note**: As of the latest version, demonstration scripts include automatic path detection and can be run directly without installation.

### API connection errors

**Solution**: Check API key and network connection. Scripts use test API by default.

### Scripts run too fast

**Solution**: Scripts include interactive prompts. Press ENTER to continue between sections.

---

## Related Documentation

- [Workflow Guide](../docs/workflow.md) - Complete batch operations workflow
- [REST API Basics](../docs/rest_api_basics.md) - HTTP methods explained
- [PATCH vs PUT](../docs/patch_vs_put.md) - Why PATCH is limited
- [Troubleshooting](../docs/troubleshooting.md) - Common issues

---

**Ready to demonstrate?** Start with `complete_nakala_lifecycle_demo.py` for a comprehensive overview!
