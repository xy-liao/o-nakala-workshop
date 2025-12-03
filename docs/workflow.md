# NAKALA API Batch Operations Workflow

## Overview

This document describes the universal workflow for batch operations with the NAKALA API, applicable to any research data management scenario.

---

## Visual Workflow

![NAKALA Batch Operations Workflow](workflow_diagram.png)

---

## Three-Stage Process

### Stage 1: Batch Import

**Purpose**: Create datasets and collections from CSV files

**Input**: 
- CSV files with dataset metadata
- CSV files with collection metadata
- Files to upload

**Process**:
1. Upload files to NAKALA (`POST /datas/uploads`)
2. Create datasets (`POST /datas`)
3. Create collections (`POST /collections`)
4. Link datasets to collections
5. Generate CSVs with assigned resource IDs

**Output**:
- CSV files with resource IDs for modification
- CSV files with resource IDs for deletion

---

### Stage 2: Batch Modify

**Purpose**: Update metadata for existing resources

**Input**:
- CSV files with resource IDs
- Updated metadata values

**Process**:
1. Read CSV data
2. For each resource:
   - Retrieve current metadata (`GET /datas/{id}`)
   - Apply updates (`PATCH` or `PUT /datas/{id}`)
3. Verify changes

**Output**:
- Updated resources on NAKALA

---

### Stage 3: Batch Delete

**Purpose**: Remove resources from NAKALA

**Input**:
- CSV files with resource IDs to delete

**Process**:
1. Read CSV data
2. For each resource:
   - Verify resource status (`GET /datas/{id}`)
   - Delete resource (`DELETE /datas/{id}`)
3. Confirm deletions

**Output**:
- Resources removed from NAKALA

---

## API Operations Reference

### Stage 1: Import Operations

| Operation | HTTP Method | Endpoint | Description |
|-----------|-------------|----------|-------------|
| Upload file | POST | `/datas/uploads` | Upload file to temporary storage |
| Create dataset | POST | `/datas` | Create new dataset with metadata |
| Create collection | POST | `/collections` | Create new collection |
| Add to collection | POST | `/collections/{id}/datas` | Link dataset(s) to collection (body: array of IDs) |

### Stage 2: Modify Operations

| Operation | HTTP Method | Endpoint | Description |
|-----------|-------------|----------|-------------|
| Get metadata | GET | `/datas/{id}` | Retrieve current metadata |
| Update metadata | PATCH/PUT | `/datas/{id}` | Update dataset metadata |
| Verify changes | GET | `/datas/{id}` | Confirm updates applied |

### Stage 3: Delete Operations

| Operation | HTTP Method | Endpoint | Description |
|-----------|-------------|----------|-------------|
| Check status | GET | `/datas/{id}` | Verify resource status |
| Delete dataset | DELETE | `/datas/{id}` | Remove dataset (pending only) |
| Delete collection | DELETE | `/collections/{id}` | Remove collection |

---

## Key Principles

1. **CSV-Driven**: All batch operations use CSV files for data input/output
2. **ID Propagation**: Stage 1 generates resource IDs used in Stages 2 & 3
3. **Sequential**: Stages must execute in order (1 → 2 → 3)
4. **API-Based**: All operations use NAKALA REST API endpoints
5. **Reversible**: Stage 3 provides cleanup capability

---

## Data Flow

```
CSV Input Files
      ↓
  NAKALA API
      ↓
Generated CSV Files (with IDs)
      ↓
  NAKALA API (modifications)
      ↓
Updated Resources
      ↓
  NAKALA API (deletions)
      ↓
Clean Environment
```

---

## Use Cases

This workflow applies to:

- ✅ Research data management
- ✅ Digital humanities projects
- ✅ Archive digitization
- ✅ Collection migration
- ✅ Metadata batch updates
- ✅ Repository management
- ✅ Any NAKALA batch operations

---

## Mermaid Diagram

For embedding in documentation or presentations:

```mermaid
flowchart TD
    Start([Start]) --> Stage1
    
    subgraph Stage1["Stage 1: Batch Import"]
        Input1[CSV Files<br/>Dataset Metadata<br/>Collection Metadata] --> Upload[Upload Files<br/>to NAKALA]
        Upload --> CreateD[Create Datasets<br/>via API]
        CreateD --> CreateC[Create Collections<br/>via API]
        CreateC --> Generate[Generate CSVs<br/>with Resource IDs]
        Generate --> Output1[CSV Files<br/>Modification List<br/>Deletion List]
    end
    
    Output1 --> Input2
    
    subgraph Stage2["Stage 2: Batch Modify"]
        Input2[CSV Files<br/>Resource IDs<br/>Updated Metadata] --> Read2[Read CSV Data]
        Read2 --> Update[Update Metadata<br/>via API]
        Update --> Output2[Updated Resources<br/>on NAKALA]
    end
    
    Output2 --> Input3
    
    subgraph Stage3["Stage 3: Batch Delete"]
        Input3[CSV Files<br/>Resource IDs] --> Read3[Read CSV Data]
        Read3 --> Delete[Delete Resources<br/>via API]
        Delete --> Output3[Resources Removed<br/>from NAKALA]
    end
    
    Output3 --> End([Complete])
    
    style Stage1 fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style Stage2 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style Stage3 fill:#f5f5f5,stroke:#616161,stroke-width:2px
    style Start fill:#fff9c4,stroke:#f57f17
    style End fill:#fff9c4,stroke:#f57f17
```

---

## Related Documentation

- [CSV Format Guide](csv_format_guide.md) - CSV file specifications
- [Quick Reference](quick_reference.md) - API basics and mandatory fields
- [REST API Basics](rest_api_basics.md) - HTTP methods and concepts
- [PATCH vs PUT](patch_vs_put.md) - Understanding modification operations
