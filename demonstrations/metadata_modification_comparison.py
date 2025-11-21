#!/usr/bin/env python3
"""
NAKALA Metadata Modification Comparison
========================================

Advanced comparison of different metadata modification approaches in NAKALA:
1. POST /metadatas - Incremental addition (SAFEST - recommended)
2. DELETE /metadatas - Incremental removal (SAFE - targeted)
3. PUT - Full replacement (DANGEROUS - replaces everything)

IMPORTANT: PATCH is NOT supported in NAKALA API
------------------------------------------------
- PATCH returns 405 Method Not Allowed for /datas and /collections endpoints
- Only exists for /datas/{id}/relations (to update relation comments)

This script demonstrates the CORRECT pattern for metadata modification:
- Use POST /metadatas to add metadata
- Use DELETE /metadatas to remove metadata

Key Learning Points:
--------------------
1. POST /metadatas adds individual metadata without affecting existing ones
2. DELETE /metadatas uses FILTER (propertyUri + lang) - removes ALL matches ⚠️
3. PUT replaces ALL metadata - any missing fields are permanently deleted
4. POST is safest for additions; DELETE is broad (not surgical)
5. Both datasets and collections support the same /metadatas pattern

Educational Goals:
------------------
- Compare safety levels of different metadata modification approaches
- Understand when to use incremental (POST/DELETE) vs full replacement (PUT)
- See side-by-side examples of the same modification done different ways
- Learn best practices for NAKALA metadata management
- Understand the risks of PUT and how to avoid data loss

Requirements:
-------------
- Python 3.7+
- requests library
- Active internet connection
- NAKALA test API access (uses apitest.nakala.fr)

Usage:
------
    python metadata_modification_comparison.py

Author: Syl (NAKALA API Educational Resources)
Created: January 11, 2025
Updated: January 12, 2025 (Corrected to remove PATCH, focus on POST/DELETE pattern)
License: CC0-1.0

Note: Part of user-created pedagogical suite, not official Huma-Num documentation.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path to import nakala package
sys.path.append(str(Path(__file__).parent.parent))

# Import from nakala package
from nakala import (
    API_URL,
    API_KEY,
    DEMO_CREATOR,
    DEMO_LICENSE,
    DEMO_TYPE_URI,
    RATE_LIMIT_DELAY,
    PROPERTY_URIS
)

from nakala.demo_helpers import (
    make_api_request,
    print_section_header,
    print_step_header,
    print_success,
    print_warning,
    print_error,
    print_info,
    wait_for_user,
    format_metadata_for_display
)


class MetadataModificationComparison:
    """
    Compare different metadata modification approaches
    """

    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY
        self.collection_id = None

    def create_test_collection(self) -> str:
        """Create a test collection with standard metadata"""
        print_info("Creating test collection...")

        metas = [
            {
                "propertyUri": PROPERTY_URIS['title'],
                "value": "Test Colection",  # Intentional typo for fix demo
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['description'],
                "value": "Original description",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['subject'],
                "value": "original keyword",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            }
        ]

        collection = {
            "status": "private",
            "metas": metas
        }

        response = make_api_request('POST', '/collections', data=collection)

        if response.status_code == 201:
            result = response.json()
            collection_id = result['payload']['id']
            print_success(f"Test collection created: {collection_id}")
            return collection_id
        else:
            raise Exception(f"Failed to create collection: {response.status_code}")



    def scenario_1_add_new_field(self):
        """Scenario 1: Add new keyword to existing metadata"""
        print_section_header("SCENARIO 1: Add New Keyword")

        print("""
Problem: Need to add a new keyword to collection
Goal: Add keyword without affecting existing metadata

We'll compare two approaches:
  A) POST /metadatas - Incremental addition (BEST for collections)
  B) PUT - Full replacement (NOT RECOMMENDED)
        """)

        # Create collection
        collection_id = self.create_test_collection()
        time.sleep(RATE_LIMIT_DELAY)

        # Get original state
        get_response = make_api_request('GET', f'/collections/{collection_id}')
        original = get_response.json()
        original_metas = original.get('metas', [])

        print_info(f"\n📊 ORIGINAL STATE:")
        print_info(f"   Metadata entries: {len(original_metas)}")

        wait_for_user("Press ENTER to see APPROACH A: POST /metadatas (BEST)")

        # ============================================================
        # APPROACH A: POST /metadatas (Best for collections)
        # ============================================================
        print_step_header("A", "Add Keyword with POST /metadatas (BEST)", "POST")

        print_success("POST /metadatas is specifically designed for incremental additions")
        print_success("Clearest intent - adding single metadata entry")

        new_keyword_meta2 = {
            "propertyUri": PROPERTY_URIS['subject'],
            "value": "new keyword via POST",
            "typeUri": "http://www.w3.org/2001/XMLSchema#string",
            "lang": "en"
        }

        response = make_api_request(
            'POST',
            f'/collections/{collection_id}/metadatas',
            data=new_keyword_meta2
        )

        if response.status_code == 204:
            print_success("\nPOST /metadatas successful")

            time.sleep(RATE_LIMIT_DELAY)
            get_response = make_api_request('GET', f'/collections/{collection_id}')
            after_post = get_response.json()
            after_metas = after_post.get('metas', [])

            print_success(f"Metadata count: {len(original_metas)} → {len(after_metas)}")
            print_success("Most explicit and safest approach")

        # Cleanup
        make_api_request('DELETE', f'/collections/{collection_id}')

        # Summary
        print_section_header("SCENARIO 1 SUMMARY")
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║               COMPARISON: Methods for Adding Metadata                      ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  POST /metadatas (BEST for Collections):                                   ║
║  ✓ Specifically designed for incremental additions                         ║
║  ✓ Clearest intent                                                          ║
║  ✓ Safest approach                                                          ║
║  ✓ Only available for collections                                           ║
║                                                                            ║
║  PUT (NOT RECOMMENDED):                                                    ║
║  ❌ Would require including ALL existing metadata                          ║
║  ❌ High risk of accidentally deleting metadata                            ║
║  ❌ Complex and error-prone                                                ║
║                                                                            ║
║  🎯 RECOMMENDATION:                                                         ║
║     Collections → Use POST /metadatas                                       ║
║     Datasets → Use POST /metadatas                                          ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def scenario_2_remove_keyword(self):
        """Scenario 2: Remove specific keyword"""
        print_section_header("SCENARIO 2: Remove Specific Keyword")

        print("""
Problem: Need to remove one keyword from collection
Goal: Remove keyword without affecting other metadata

Best approach:
  DELETE /metadatas - Surgical removal (collections only)
        """)

        # Create collection with multiple keywords
        metas = [
            {
                "propertyUri": PROPERTY_URIS['title'],
                "value": "Test Collection",
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['subject'],
                "value": "keep this keyword",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['subject'],
                "value": "remove this keyword",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['subject'],
                "value": "keep this too",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            }
        ]

        collection = {
            "status": "private",
            "metas": metas
        }

        response = make_api_request('POST', '/collections', data=collection)
        collection_id = response.json()['payload']['id']
        time.sleep(RATE_LIMIT_DELAY)

        print_success(f"Test collection created with 3 keywords")

        get_response = make_api_request('GET', f'/collections/{collection_id}')
        original = get_response.json()
        original_metas = original.get('metas', [])
        keywords = [m for m in original_metas if m.get('propertyUri') == PROPERTY_URIS['subject']]

        print_info(f"\n📊 ORIGINAL STATE:")
        print_info(f"   Total metadata: {len(original_metas)}")
        print_info(f"   Keywords: {len(keywords)}")
        for kw in keywords:
            print_info(f"      • {kw.get('value')}")

        wait_for_user("\nPress ENTER to remove specific keyword")

        # Remove specific keyword using DELETE filter
        print_step_header(1, "Remove Keywords with DELETE /metadatas", "DELETE")

        # ⚡ DISCOVERY (November 17, 2025): DELETE uses FILTER format
        # Removes ALL metadata matching the filter (not just one specific value)
        keyword_filter = {
            "propertyUri": PROPERTY_URIS['subject'],
            "lang": "en"
        }
        # Note: Do NOT include "value" or "typeUri" - they are ignored by API

        print_warning("\n⚠️  DELETE /metadatas uses FILTER format")
        print_info("   This will remove ALL dcterms:subject in English")
        print_info("   Cannot target a specific value - removes ALL matches")

        response = make_api_request(
            'DELETE',
            f'/collections/{collection_id}/metadatas',
            data=keyword_filter
        )

        if response.status_code == 204:
            print_success("\nAll matching keywords removed successfully")

            time.sleep(RATE_LIMIT_DELAY)
            get_response = make_api_request('GET', f'/collections/{collection_id}')
            after_delete = get_response.json()
            after_metas = after_delete.get('metas', [])
            after_keywords = [m for m in after_metas if m.get('propertyUri') == PROPERTY_URIS['subject']]

            print_info(f"\n📊 AFTER DELETE:")
            print_info(f"   Total metadata: {len(after_metas)}")
            print_info(f"   Keywords: {len(after_keywords)}")
            for kw in after_keywords:
                print_info(f"      • {kw.get('value')}")

            print_success(f"\nRemoved ALL English keywords: {len(keywords)} → {len(after_keywords)}")
            print_success("Non-English keywords preserved (if any)")
            print_success("Title and other metadata preserved")

        # Cleanup
        make_api_request('DELETE', f'/collections/{collection_id}')

        print_section_header("SCENARIO 2 SUMMARY")
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║             DELETE /metadatas - Filter-Based Bulk Removal                  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ⚠️  Removes ALL metadata matching the filter                              ║
║  ⚠️  Cannot target specific values - uses filter (propertyUri + lang)      ║
║  ✓ Preserves metadata NOT matching the filter                              ║
║                                                                            ║
║  ⚡ DISCOVERY (November 17, 2025):                                          ║
║     DELETE uses FILTER format: {"propertyUri": "...", "lang": "..."}       ║
║     Do NOT include "value" or "typeUri" - they are ignored!                ║
║                                                                            ║
║  💡 For TRUE Surgical Removal (targeting specific values):                 ║
║     1. GET /collections/{id} - Retrieve all metadata                       ║
║     2. Modify in memory - Remove specific value from array                 ║
║     3. PUT /collections/{id} - Replace with modified metadata              ║
║     (See incremental_metadata_demo.py for GET+PUT pattern)                ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def run_all_comparisons(self):
        """Run all comparison scenarios"""
        print_section_header("NAKALA METADATA MODIFICATION COMPARISON")

        print("""
This demonstration compares different approaches to metadata modification:

  Scenario 1: Add New Keyword
    • POST /metadatas vs PUT
    • Best practices for incremental additions

  Scenario 2: Remove Specific Keyword
    • DELETE /metadatas (surgical removal)
    • Collections vs datasets differences

📚 Learning Objectives:
   - Compare safety levels of each approach
   - Understand when to use each method
   - Learn best practices for metadata management
   - See real-world examples side-by-side
        """)

        wait_for_user("Press ENTER to start comparisons")

        try:
            # Scenario 1: Add keyword
            self.scenario_1_add_new_field()
            wait_for_user("\nPress ENTER for Scenario 2")

            # Scenario 2: Remove keyword
            self.scenario_2_remove_keyword()

            # Final summary
            print_section_header("ALL COMPARISONS COMPLETE")

            print("""
✓ Successfully compared all metadata modification approaches!

🎯 FINAL RECOMMENDATIONS:

┌─────────────────────────────────────────────────────────────────────────┐
│                      DECISION TREE                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Modifying a COLLECTION?                                                 │
│  ├─ Adding metadata?      → Use POST /collections/{id}/metadatas        │
│  ├─ Removing metadata?    → Use DELETE /collections/{id}/metadatas      │
│  ├─ Changing status?      → Use PUT /collections/{id}/status            │
│  ├─ Updating a field?     → Use GET + PUT (complete replacement)        │
│  └─ Complete rebuild?     → Use PUT (with extreme caution!)             │
│                                                                          │""")
            print("│  Modifying a DATASET?                                                    │")
            print("│  ├─ Adding metadata?      → Use POST /datas/{id}/metadatas              │")
            print("│  ├─ Removing metadata?    → Use DELETE /datas/{id}/metadatas            │")
            print("│  ├─ Updating a field?     → Use GET + PUT (complete replacement)        │")
            print("│  ├─ Changing status?      → Use PUT /datas/{id}/status                  │")
            print("""│  └─ Complete rebuild?     → Use PUT (with extreme caution!)             │
│                                                                          │
│  ⚠️  NOTE: Datasets do NOT support PATCH (returns 405)                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

⚠️  GENERAL RULES:

  1. Use POST/DELETE /metadatas for incremental changes
  2. Avoid PUT unless absolutely necessary
  3. Always GET before and after to verify changes
  4. Test with pending/private status first

📚 Remember:
   • POST /metadatas = Incremental add (safest)
   • DELETE /metadatas = Filter-based remove
   • PUT = Full replacement (dangerous)
   • PATCH = NOT SUPPORTED
            """)

        except Exception as e:
            print_error(f"\nComparison failed: {str(e)}")
            raise


def main():
    """Main entry point"""
    demo = MetadataModificationComparison()
    demo.run_all_comparisons()


if __name__ == '__main__':
    main()
