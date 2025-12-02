#!/usr/bin/env python3
"""
NAKALA Collection Lifecycle Demonstration
=========================================

Complete demonstration of HTTP method lifecycle for NAKALA collections:
- POST: Create collection and add metadata
- GET: Retrieve collection state
- POST /metadatas: Add metadata incrementally (safe)
- DELETE /metadatas: Remove specific metadata (safe)
- PUT: Full replacement (dangerous - replaces everything)
- POST /datas: Dataset affectation (link dataset to collection)
- DELETE /datas: Dataset désaffectation (unlink dataset from collection)
- PATCH /status: Change collection status
- DELETE: Remove collection entirely

Key Learning Points:
--------------------
1. Collections do NOT support PATCH on main endpoint (/collections/{id})
   - Use POST/DELETE /collections/{id}/metadatas for incremental updates
   - Or use PUT /collections/{id}/status for safe status changes
2. Use POST/DELETE /metadatas for incremental metadata operations (safest)
3. Understand affectation (linking) vs désaffectation (unlinking) datasets
4. PUT replaces ALL metadata - use with extreme caution
5. Collections can be deleted anytime (unlike published datasets)

Educational Goals:
------------------
1. Master incremental metadata operations with /metadatas sub-endpoint
2. Learn désaffectation (remove from collection) vs deletion
3. Practice safe metadata updates (POST/DELETE vs dangerous PUT)
4. Understand dataset linking/unlinking workflows
5. Compare collection vs dataset capabilities

Requirements:
-------------
- Python 3.7+
- requests library
- Active internet connection
- NAKALA test API access (uses apitest.nakala.fr)

Usage:
------
    python collection_lifecycle_demo.py

Author: Syl (NAKALA API Educational Resources)
Created: January 11, 2025
Updated: January 12, 2025 (Corrected PATCH documentation)
License: CC0-1.0

Note: Part of user-created pedagogical suite, not official Huma-Num documentation.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path to allow importing nakala package
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import from nakala package
from nakala import (
    API_URL,
    API_KEY,
    DEMO_CREATOR,
    DEMO_LICENSE,
    DEMO_TYPE_URI,
    RATE_LIMIT_DELAY,
    CsvConverter
)

from nakala.demo_helpers import (
    make_api_request,
    print_section_header,
    print_step_header,
    print_success,
    print_warning,
    print_error,
    print_info,
    print_json_comparison,
    wait_for_user,
    print_method_comparison_table,
    format_metadata_for_display
)


class CollectionLifecycleDemo:
    """
    Step-by-step demonstration of NAKALA collection lifecycle
    """

    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY
        self.converter = CsvConverter()
        self.collection_id = None
        self.dataset_id = None

    def step_1_post_create_collection(self):
        """Step 1: POST - Create new collection"""
        print_step_header(1, "Create New Collection", "POST")

        print_info("Creating a collection with minimal metadata...")

        # Prepare metadata
        metas = [
            {
                "propertyUri": self.converter.property_uris['title'],
                "value": "Demo Collection - Lifecycle Test",
                "lang": "en"
            },
            {
                "propertyUri": self.converter.property_uris['description'],
                "value": "This collection demonstrates HTTP method lifecycle",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            }
        ]

        collection = {
            "status": "private",
            "metas": metas
        }

        print_info("\n📦 Collection payload:")
        print_info(f"   Status: {collection['status']}")
        print_info(f"   Metadata fields: {len(metas)}")
        print_info("\n📋 Metadata:")
        print_info(format_metadata_for_display(metas))

        # Create collection
        response = make_api_request('POST', '/collections', data=collection)

        if response.status_code == 201:
            result = response.json()
            self.collection_id = result['payload']['id']
            print_success(f"Collection created successfully!")
            print_info(f"   Collection ID: {self.collection_id}")
            status = result['payload'].get('status', 'N/A')
            if status != 'N/A':
                print_info(f"   Status: {status}")
            return result['payload']
        else:
            print_error(f"Failed to create collection: {response.status_code}")
            print_error(f"Response: {response.text}")
            raise Exception("Collection creation failed")

    def step_2_post_add_metadata_incremental(self):
        """Step 2: POST /metadatas - Add metadata incrementally (safer than PUT)"""
        print_step_header(2, "Add Metadata Incrementally", "POST /metadatas")

        print_info("Adding individual metadata entries without affecting existing metadata")
        print_success("This is SAFER than PUT because it doesn't replace everything")

        # Add keywords one by one
        keywords = ["API demonstration", "Collection lifecycle", "HTTP methods"]

        for keyword in keywords:
            meta = {
                "propertyUri": self.converter.property_uris['subject'],
                "value": keyword,
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            }

            print_info(f"\nAdding keyword: '{keyword}'")
            response = make_api_request(
                'POST',
                f'/collections/{self.collection_id}/metadatas',
                data=meta
            )

            if response.status_code in [201, 204]:
                print_success(f"Added: {keyword}")
            else:
                print_error(f"✗ Failed to add keyword: {response.status_code}")

            time.sleep(RATE_LIMIT_DELAY)

        # Verify
        get_response = make_api_request('GET', f'/collections/{self.collection_id}')
        if get_response.status_code == 200:
            collection = get_response.json()
            print_success(f"\nTotal metadata entries now: {len(collection.get('metas', []))}")
            print_success("Original metadata (title, description) preserved")

    def step_3_create_and_link_dataset(self):
        """Step 3: SKIPPED - Dataset Creation (Requires File Upload)"""
        print_step_header(3, "Create Dataset & Link to Collection", "POST")

        print_warning("SKIPPED: Dataset creation requires file upload")
        print_info("NAKALA's /datas endpoint requires 'files' array with at least one file")
        print_info("Cannot create datasets with empty files: [] - returns 422 error")
        print_info("")
        print_info("Collections can exist independently without datasets")
        print_info("For complete file upload → dataset creation workflow:")
        print_info("  → See dataset_lifecycle_demo.py")
        print_info("")
        print_info("This demo focuses on COLLECTION-specific operations:")
        print_info("  • Metadata management (POST/DELETE /metadatas)")
        print_info("  • Status updates")
        print_info("  • PUT vs incremental operations")

        # Set dataset_id to None explicitly
        self.dataset_id = None

    def step_4_patch_update_status(self, before_state: Dict[str, Any]):
        """Step 4: Update Collection Status (Using PUT /status)"""
        print_step_header(4, "Update Collection Status", "PUT /status/{status}")

        print_warning("Note: PATCH /collections/{id} is NOT supported (returns 405)")
        print_success(" Using PUT /collections/{id}/status/{status} instead")
        print_info("\nChanging collection status from 'private' to 'public'")
        print_info("This endpoint only modifies status, preserving all metadata")

        response = make_api_request(
            'PUT',
            f'/collections/{self.collection_id}/status/public'
        )

        if response.status_code == 204:
            print_success("Status updated to 'public'")

            # Verify
            time.sleep(RATE_LIMIT_DELAY)
            get_response = make_api_request('GET', f'/collections/{self.collection_id}')
            if get_response.status_code == 200:
                after_state = get_response.json()
                before_status = before_state.get('status', 'unknown')
                after_status = after_state.get('status', 'unknown')
                print_success(f"\nStatus changed: {before_status} → {after_status}")
                print_success(f"Metadata preserved: {len(after_state.get('metas', []))} entries")
                print_success(f"Datasets preserved: {len(after_state.get('datas', []))} linked")
                return after_state
        else:
            print_error(f"Status update failed: {response.status_code}")

    def step_5_desaffectation(self):
        """Step 5: SKIPPED - Remove Dataset from Collection (Désaffectation)"""
        print_step_header(5, "Remove Dataset from Collection (Désaffectation)", "DELETE /datas")

        print_warning("SKIPPED: No dataset to remove (Step 3 was skipped)")
        print_info("")
        print_info("🎓 EDUCATIONAL NOTE: Désaffectation vs Deletion")
        print_info("=" * 70)
        print_info("")
        print_info("DÉSAFFECTATION (DELETE /datas/{id}/collections):")
        print_info("  • Removes dataset FROM collection")
        print_info("  • Dataset STILL EXISTS on server")
        print_info("  • Can be re-added to collection later")
        print_info("  • Reversible operation")
        print_info("")
        print_info("DELETION (DELETE /datas/{id}):")
        print_info("  • Deletes dataset FROM SERVER entirely")
        print_info("  • Dataset NO LONGER EXISTS")
        print_info("  • Cannot be recovered")
        print_info("  • Permanent and irreversible")
        print_info("  • Only works on pending datasets")
        print_info("")
        print_info("For full demonstration:")
        print_info("  → Run dataset_lifecycle_demo.py with file uploads")

    def step_6_delete_metadata_incremental(self):
        """Step 6: DELETE /metadatas - Remove specific metadata entry"""
        print_step_header(6, "Remove Specific Metadata Entry", "DELETE /metadatas")

        print_info("Removing one keyword while preserving others...")

        # First, get current metadata to find a keyword to remove
        get_response = make_api_request('GET', f'/collections/{self.collection_id}')
        if get_response.status_code == 200:
            collection = get_response.json()
            metas = collection.get('metas', [])

            # Find first keyword
            keyword_meta = next(
                (m for m in metas if m.get('propertyUri') == self.converter.property_uris['subject']),
                None
            )

            if keyword_meta:
                keyword_value = keyword_meta.get('value')
                print_warning(f"\n⚠️  Removing ALL keywords matching filter")
                print_info(f"   Current keyword to filter: '{keyword_value}'")

                # ⚡ DISCOVERY (November 17, 2025): DELETE uses FILTER format
                # Removes ALL metadata matching the filter (not just one value)
                delete_filter = {
                    "propertyUri": keyword_meta['propertyUri']
                }

                # Add language filter if present (more selective)
                if 'lang' in keyword_meta:
                    delete_filter['lang'] = keyword_meta['lang']

                # Note: Do NOT include "value" or "typeUri" - they are ignored by API
                # This will remove ALL keywords (dcterms:subject) with matching lang

                print_info(f"\n📦 DELETE filter: {delete_filter}")
                print_warning("   This removes ALL keywords with this propertyUri + lang")

                delete_response = make_api_request(
                    'DELETE',
                    f'/collections/{self.collection_id}/metadatas',
                    data=delete_filter
                )

                if delete_response.status_code in [200, 204]:
                    print_success("All matching keywords removed")

                    time.sleep(RATE_LIMIT_DELAY)

                    # Verify
                    verify_response = make_api_request('GET', f'/collections/{self.collection_id}')
                    if verify_response.status_code == 200:
                        updated_collection = verify_response.json()
                        updated_metas = updated_collection.get('metas', [])
                        print_success(f"Metadata count: {len(metas)} → {len(updated_metas)}")
                        print_success("Other metadata preserved")
                else:
                    print_error(f"Delete metadata failed: {delete_response.status_code}")
                    print_info(f"Response: {delete_response.text[:200]}")
            else:
                print_warning("No keywords found to delete")

    def step_7_put_full_replacement(self, before_state: Dict[str, Any]):
        """Step 7: PUT - Complete replacement (demonstrates data loss)"""
        print_step_header(7, "Full Replacement - DANGEROUS!", "PUT")

        print_warning("PUT REPLACES EVERYTHING IN COLLECTION!")
        print_warning("Any metadata, datasets not included will be DELETED!")

        # Minimal collection data
        minimal_metas = [
            {
                "propertyUri": self.converter.property_uris['title'],
                "value": "Demo Collection - PUT Replacement",
                "lang": "en"
            }
        ]

        put_data = {
            "status": "public",
            "metas": minimal_metas
            # Note: NOT including 'datas' field, NOT including description, keywords
        }

        print_info(f"\n📦 PUT payload:")
        print_info(f"   Metadata BEFORE: {len(before_state.get('metas', []))} entries")
        print_info(f"   Metadata in PUT: {len(minimal_metas)} entries")
        print_warning("   Missing: description, keywords, datasets (will be REMOVED!)")

        response = make_api_request('PUT', f'/collections/{self.collection_id}', data=put_data)

        if response.status_code == 204:
            print_warning("PUT successful - but data was lost!")

            # Get updated state
            time.sleep(RATE_LIMIT_DELAY)
            get_response = make_api_request('GET', f'/collections/{self.collection_id}')
            after_state = get_response.json()

            # Calculate actual values for comparison
            before_has_desc = any('description' in m.get('propertyUri', '') for m in before_state.get('metas', []))
            before_has_keywords = any('subject' in m.get('propertyUri', '') for m in before_state.get('metas', []))
            after_has_desc = any('description' in m.get('propertyUri', '') for m in after_state.get('metas', []))
            after_has_keywords = any('subject' in m.get('propertyUri', '') for m in after_state.get('metas', []))

            print_json_comparison(
                {
                    "metadata_count": len(before_state.get('metas', [])),
                    "dataset_count": len(before_state.get('datas', [])),
                    "has_description": before_has_desc,
                    "has_keywords": before_has_keywords
                },
                {
                    "metadata_count": len(after_state.get('metas', [])),
                    "dataset_count": len(after_state.get('datas', [])),
                    "has_description": after_has_desc,
                    "has_keywords": after_has_keywords
                },
                "PUT RESULT - Data Loss Demonstration"
            )

            meta_lost = len(before_state.get('metas', [])) - len(after_state.get('metas', []))
            if meta_lost > 0:
                print_error(f"\nLost {meta_lost} metadata entries!")
                if before_has_desc and not after_has_desc:
                    print_error("Description: DELETED")
                if before_has_keywords and not after_has_keywords:
                    print_error("Keywords: DELETED")
                print_success("Only fields in PUT payload survived")

            print_warning("\nKEY LESSON: For collections, use POST/DELETE /metadatas instead of PUT!")

            return after_state
        else:
            print_error(f"PUT failed: {response.status_code}")

    def step_8_delete_collection(self):
        """Step 8: DELETE - Remove entire collection"""
        print_step_header(8, "Delete Entire Collection", "DELETE")

        print_info("Deleting the collection (permanent)...")
        print_warning("Note: This does NOT delete datasets that were in the collection")

        response = make_api_request('DELETE', f'/collections/{self.collection_id}')

        if response.status_code == 204:
            print_success("Collection deleted successfully")

            time.sleep(RATE_LIMIT_DELAY)

            # Verify deletion
            get_response = make_api_request('GET', f'/collections/{self.collection_id}')

            if get_response.status_code == 404:
                print_success("Confirmed: Collection no longer exists")

                # Verify dataset still exists
                if self.dataset_id:
                    print_info("\nVerifying dataset still exists...")
                    dataset_response = make_api_request('GET', f'/datas/{self.dataset_id}')

                    if dataset_response.status_code == 200:
                        print_success("Dataset still exists (collection deletion doesn't delete datasets)")

                        # Clean up dataset
                        print_info("\nCleaning up test dataset...")
                        delete_dataset_response = make_api_request('DELETE', f'/datas/{self.dataset_id}')
                        if delete_dataset_response.status_code == 204:
                            print_success("Test dataset cleaned up")
            else:
                print_warning(f"Collection check returned: {get_response.status_code}")
        else:
            print_error(f"DELETE failed: {response.status_code}")

    def run_complete_lifecycle(self):
        """Execute complete collection lifecycle demonstration"""
        print_section_header("NAKALA COLLECTION LIFECYCLE DEMONSTRATION")

        print("""
This demonstration shows the complete HTTP method lifecycle for NAKALA collections:

  1. POST             - Create collection
  2. POST /metadatas  - Add metadata incrementally (safe)
  3. POST /datas      - Link dataset to collection (affectation)
  4. PUT /status      - Update status (safe, targeted endpoint)
  5. DELETE /datas    - Remove dataset from collection (désaffectation)
  6. DELETE /metadatas - Remove specific metadata entry
  7. PUT              - Full replacement (dangerous - shows data loss)
  8. DELETE           - Delete entire collection

📚 Learning Objectives:
   - Understand collection-specific operations
   - Learn désaffectation vs deletion
   - See incremental metadata operations
   - Practice dataset linking/unlinking
   - Compare PATCH vs PUT
        """)

        wait_for_user("Press ENTER to start demonstration")

        try:
            # Step 1: Create collection
            self.step_1_post_create_collection()
            wait_for_user()

            # Step 2: Add metadata incrementally
            self.step_2_post_add_metadata_incremental()
            wait_for_user()

            # Step 3: Create and link dataset
            self.step_3_create_and_link_dataset()
            wait_for_user()

            # Get state before PATCH
            get_response = make_api_request('GET', f'/collections/{self.collection_id}')
            state_before_patch = get_response.json()

            # Step 4: PATCH update status
            state_after_patch = self.step_4_patch_update_status(state_before_patch)
            wait_for_user()

            # Step 5: Désaffectation
            self.step_5_desaffectation()
            wait_for_user()

            # Step 6: Delete metadata entry
            self.step_6_delete_metadata_incremental()
            wait_for_user()

            # Get state before PUT
            get_response = make_api_request('GET', f'/collections/{self.collection_id}')
            state_before_put = get_response.json()

            # Step 7: PUT full replacement
            state_after_put = self.step_7_put_full_replacement(state_before_put)
            wait_for_user()

            # Step 8: Delete collection
            self.step_8_delete_collection()

            # Final summary
            print_section_header("DEMONSTRATION COMPLETE")

            print("""
✓ Successfully demonstrated all collection operations!

📚 KEY TAKEAWAYS:

1. POST /collections - Create collection
   ✓ Returns collection ID
   ✓ Can start with minimal metadata

2. POST /collections/{id}/metadatas - Add metadata incrementally
   ✓ SAFER than PUT (doesn't replace)
   ✓ Preserves existing metadata
   ✓ Best for adding fields

3. POST /collections/{id}/datas/{dataId} - Affectation
   ✓ Links dataset to collection
   ✓ Dataset can be in multiple collections

4. PUT /collections/{id}/status/{status} - Update status
   ✓ Only modifies status field
   ✓ Preserves all metadata and datasets
   ✓ Safe, targeted operation
   
   Note: PATCH /collections/{id} is NOT supported (returns 405)
   (Use PUT /collections/{id}/status for status changes)

5. DELETE /collections/{id}/datas/{dataId} - Désaffectation
   ✓ Removes dataset from collection
   ✗ Does NOT delete dataset from server
   ✓ Dataset still exists independently

6. DELETE /collections/{id}/metadatas - Remove metadata
   ✓ Removes specific metadata entry
   ✓ Preserves other metadata

7. PUT /collections/{id} - Full replacement
   ⚠️  DANGEROUS - replaces everything
   ⚠️  Any missing fields are DELETED
   ⚠️  Avoid using PUT on collections

8. DELETE /collections/{id} - Delete collection
   ✓ Permanent deletion
   ✗ Does NOT delete datasets in collection
   ⚠️  Irreversible

🎯 BEST PRACTICES:
   - Use POST/DELETE /metadatas for metadata (not PUT)
   - Use PATCH for status changes
   - Remember: Désaffectation ≠ Deletion
   - Always verify changes with GET
   - Design deletion strategy early
            """)

            print_method_comparison_table()

            print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║             DÉSAFFECTATION vs DELETION (Critical Difference)               ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  DÉSAFFECTATION (DELETE /collections/{id}/datas/{dataId})                 ║
║  --------------------------------------------------------                  ║
║  • Removes dataset FROM collection                                         ║
║  • Dataset STILL EXISTS on server                                          ║
║  • Can be re-added to collection later                                     ║
║  • Reversible operation                                                    ║
║                                                                            ║
║  DELETION (DELETE /datas/{id})                                             ║
║  --------------------------------------------------------                  ║
║  • Deletes dataset FROM SERVER entirely                                    ║
║  • Dataset NO LONGER EXISTS                                                ║
║  • Cannot be recovered                                                     ║
║  • Permanent and irreversible                                              ║
║  • Only works on pending datasets                                          ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
            """)

        except Exception as e:
            print_error(f"\nDemonstration failed: {str(e)}")
            raise


def main():
    """Main entry point"""
    demo = CollectionLifecycleDemo()
    demo.run_complete_lifecycle()


if __name__ == '__main__':
    main()
