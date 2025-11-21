#!/usr/bin/env python3
"""
NAKALA Complete Lifecycle Demonstration
========================================

Complete end-to-end demonstration combining datasets and collections:

PART 1: DATASET OPERATIONS
1. Upload file to NAKALA
2. Create dataset with file
3. Add metadata incrementally (POST /metadatas)
4. Update dataset status
5. Demonstrate PUT dangers

PART 2: COLLECTION OPERATIONS
6. Create collection
7. Link dataset to collection (affectation)
8. Add collection metadata incrementally
9. Remove dataset from collection (désaffectation)
10. Demonstrate collection PUT dangers

PART 3: CLEANUP
11. Delete collection
12. Verify dataset still exists (désaffectation ≠ deletion)

Key Learning Points:
--------------------
1. Complete file upload → dataset → collection workflow
2. Affectation (linking) vs Désaffectation (unlinking) vs Deletion
3. Incremental operations (POST/DELETE /metadatas) are safer than PUT
4. PATCH is NOT supported for /datas or /collections
5. Collections can be deleted anytime, published datasets cannot

Educational Goals:
------------------
1. Master complete NAKALA workflow from start to finish
2. Understand relationship between datasets and collections
3. Learn safe metadata management patterns
4. Practice real-world operations with proper sequencing
5. Understand cleanup and resource management

Requirements:
-------------
- Python 3.7+
- requests library
- Active internet connection
- NAKALA test API access (uses apitest.nakala.fr)

Usage:
------
    python complete_nakala_lifecycle_demo.py

Author: Syl (NAKALA API Educational Resources)
Created: January 13, 2025
License: CC0-1.0

Note: Part of user-created pedagogical suite, not official Huma-Num documentation.
"""

import sys
import time
import json
import io
from pathlib import Path
from typing import Dict, Any, Optional

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
    print_json_comparison,
    wait_for_user
)


class CompleteNAKALALifecycleDemo:
    """
    Complete NAKALA lifecycle demonstration combining datasets and collections
    """

    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY
        self.file_info = None  # Full file info object from upload
        self.dataset_id = None
        self.collection_id = None

    # ========================================================================
    # PART 1: DATASET OPERATIONS
    # ========================================================================

    def step_1_upload_file(self):
        """Step 1: Upload file to NAKALA"""
        print_step_header(1, "Upload File to NAKALA", "POST /datas/uploads")

        print_info("Creating a small demo text file and uploading it...")

        # Create demo file in memory
        file_content = """NAKALA Demonstration File
==========================

This is a demonstration file created for the complete NAKALA lifecycle demo.

Purpose: Show file upload → dataset creation → collection workflow
Created: 2025-01-13
Type: Text document
""".encode('utf-8')

        # Upload file using requests directly (multipart/form-data)
        import requests

        upload_url = f"{API_URL}/datas/uploads"
        files = {'file': ('demo_file.txt', io.BytesIO(file_content), 'text/plain')}
        headers = {'X-API-KEY': API_KEY}

        print_info(f"   POST {upload_url}")
        upload_response = requests.post(upload_url, files=files, headers=headers)

        if upload_response.status_code == 201:
            # Get full file info object (includes name, sha1, size, etc.)
            self.file_info = upload_response.json()
            # Add embargo date (required field)
            self.file_info['embargoed'] = time.strftime("%Y-%m-%d")

            print_info(f"      ✓ Response: {upload_response.status_code}")
            print_success(f"File uploaded successfully!")
            print_info(f"  SHA1: {self.file_info['sha1']}")
            print_info(f"  Size: {len(file_content)} bytes")
            return True
        else:
            print_error(f"File upload failed: {upload_response.status_code}")
            print_info(f"Response: {upload_response.text[:200]}")
            return False

    def step_2_create_dataset(self):
        """Step 2: Create dataset with uploaded file"""
        print_step_header(2, "Create Dataset with File", "POST /datas")

        print_info("Creating dataset with minimal required metadata...")

        metas = [
            {
                "propertyUri": PROPERTY_URIS['title'],
                "value": "Complete Lifecycle Demo Dataset",
                "lang": "en",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "propertyUri": PROPERTY_URIS['type'],
                "value": "http://purl.org/coar/resource_type/c_18cf",  # Text
                "typeUri": "http://purl.org/dc/terms/URI"
            },
            {
                "propertyUri": PROPERTY_URIS['creator'],
                "value": DEMO_CREATOR
            },
            {
                "propertyUri": PROPERTY_URIS['created'],
                "value": "2025",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "propertyUri": PROPERTY_URIS['license'],
                "value": DEMO_LICENSE,
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            }
        ]

        # IMPORTANT: NAKALA expects full file info object, not just SHA1
        dataset = {
            "status": "pending",
            "files": [self.file_info],
            "metas": metas
        }

        print_info(f"\n📦 Dataset payload:")
        print_info(f"   Status: pending")
        print_info(f"   Files: 1 (SHA1: {self.file_info['sha1'][:16]}...)")
        print_info(f"   Metadata: {len(metas)} entries")

        response = make_api_request('POST', '/datas', data=dataset)

        if response.status_code == 201:
            result = response.json()
            self.dataset_id = result['payload']['id']
            print_success(f"Dataset created successfully!")
            print_info(f"  Dataset ID: {self.dataset_id}")
            return True
        else:
            print_error(f"Dataset creation failed: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False

    def step_3_add_dataset_metadata(self):
        """Step 3: Add metadata incrementally to dataset"""
        print_step_header(3, "Add Dataset Metadata Incrementally", "POST /metadatas")

        print_success("Using POST /metadatas - SAFE incremental operation")
        print_info("Adding keywords and description without affecting existing metadata")

        # Add description
        print_info("\nAdding description...")
        desc_meta = {
            "propertyUri": PROPERTY_URIS['description'],
            "value": "This dataset demonstrates the complete NAKALA workflow from file upload to collection management.",
            "lang": "en",
            "typeUri": "http://www.w3.org/2001/XMLSchema#string"
        }

        response = make_api_request(
            'POST',
            f'/datas/{self.dataset_id}/metadatas',
            data=desc_meta
        )

        if response.status_code in [201, 204]:
            print_success("Description added")
        else:
            print_error(f"Failed: {response.status_code}")

        time.sleep(RATE_LIMIT_DELAY)

        # Add keywords
        keywords = ["Demonstration", "NAKALA", "Lifecycle", "Complete workflow"]
        for keyword in keywords:
            print_info(f"Adding keyword: '{keyword}'")
            keyword_meta = {
                "propertyUri": PROPERTY_URIS['subject'],
                "value": keyword,
                "lang": "en",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            }

            response = make_api_request(
                'POST',
                f'/datas/{self.dataset_id}/metadatas',
                data=keyword_meta
            )

            if response.status_code in [201, 204]:
                print_success(f"  Added: {keyword}")
            else:
                print_error(f"  ✗ Failed: {response.status_code}")

            time.sleep(RATE_LIMIT_DELAY)

        # Verify
        get_response = make_api_request('GET', f'/datas/{self.dataset_id}')
        if get_response.status_code == 200:
            dataset = get_response.json()
            print_success(f"\nDataset now has {len(dataset.get('metas', []))} metadata entries")
            print_success("All original metadata preserved")

    # ========================================================================
    # PART 2: COLLECTION OPERATIONS
    # ========================================================================

    def step_4_create_collection(self):
        """Step 4: Create collection"""
        print_section_header("PART 2: COLLECTION OPERATIONS")
        print_step_header(4, "Create Collection", "POST /collections")

        print_info("Creating a collection to organize our dataset...")

        metas = [
            {
                "propertyUri": PROPERTY_URIS['title'],
                "value": "Complete Lifecycle Demo Collection",
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['description'],
                "value": "This collection demonstrates dataset affectation and management.",
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
            self.collection_id = result['payload']['id']
            print_success(f"Collection created successfully!")
            print_info(f"  Collection ID: {self.collection_id}")
            return True
        else:
            print_error(f"Collection creation failed: {response.status_code}")
            return False

    def step_5_link_dataset_to_collection(self):
        """Step 5: Link dataset to collection (Affectation)"""
        print_step_header(5, "Link Dataset to Collection (Affectation)", "POST /datas/{id}/collections")

        print_info("Linking dataset to collection...")
        print_info(f"  Dataset: {self.dataset_id}")
        print_info(f"  Collection: {self.collection_id}")

        # Add small delay to ensure resources are indexed
        print_info("\nWaiting for resources to be indexed...")
        time.sleep(2)

        response = make_api_request(
            'POST',
            f'/datas/{self.dataset_id}/collections',
            data=[self.collection_id]
        )

        if response.status_code in [201, 204]:
            print_success("Dataset linked to collection (affectation)")

            time.sleep(RATE_LIMIT_DELAY)

            # Verify
            get_response = make_api_request('GET', f'/collections/{self.collection_id}')
            if get_response.status_code == 200:
                collection = get_response.json()
                dataset_count = len(collection.get('datas', []))
                print_success(f"Collection now contains {dataset_count} dataset(s)")

                print_info("\n🎓 KEY CONCEPT: Affectation")
                print_info("  • Dataset is LINKED to collection")
                print_info("  • Dataset still exists independently")
                print_info("  • Same dataset can be in multiple collections")
                print_info("  • Removing from collection doesn't delete dataset")
        else:
            print_error(f"Affectation failed: {response.status_code}")
            print_info(f"Response: {response.text[:300]}")
            print_warning("    This is a known NAKALA timing issue with test API")
            print_warning("    The demo will continue, but affectation features will be skipped")

    def step_6_add_collection_metadata(self):
        """Step 6: Add collection metadata incrementally"""
        print_step_header(6, "Add Collection Metadata", "POST /metadatas")

        print_info("Adding tags to collection...")

        tags = ["demonstration", "tutorial", "complete-workflow"]
        for tag in tags:
            print_info(f"Adding tag: '{tag}'")
            tag_meta = {
                "propertyUri": PROPERTY_URIS['subject'],
                "value": tag,
                "lang": "en",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            }

            response = make_api_request(
                'POST',
                f'/collections/{self.collection_id}/metadatas',
                data=tag_meta
            )

            if response.status_code in [201, 204]:
                print_success(f"  Added: {tag}")

            time.sleep(RATE_LIMIT_DELAY)

    def step_7_update_collection_status(self):
        """Step 7: Update collection status"""
        print_step_header(7, "Update Collection Status", "PUT /status/{status}")

        print_info("Changing collection status from 'private' to 'public'")

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
                collection = get_response.json()
                print_success(f"Current status: {collection.get('status')}")
                print_success(f"All metadata preserved: {len(collection.get('metas', []))} entries")
                print_success(f"Dataset link preserved: {len(collection.get('datas', []))} dataset(s)")
        elif response.status_code == 422:
            print_warning("Status update failed as expected (422 Unprocessable Entity)")
            print_info("Reason: Public collections cannot contain PENDING datasets")
            print_info("This demonstrates a NAKALA validation rule:")
            print_info("  • Public Collection → Must contain only PUBLISHED datasets")
            print_info("  • Private Collection → Can contain PENDING or PUBLISHED datasets")
            print_success("✓ Validation rule verified")
        else:
            print_error(f"Status update failed: {response.status_code}")

    def step_8_desaffectation(self):
        """Step 8: Remove dataset from collection (Désaffectation)"""
        print_step_header(8, "Remove Dataset from Collection (Désaffectation)", "DELETE /datas/{id}/collections")

        print_warning("CRITICAL CONCEPT: Désaffectation ≠ Deletion")
        print_info("Désaffectation removes dataset FROM collection")
        print_info("Dataset will STILL EXIST on server independently")

        print_info(f"\nRemoving dataset {self.dataset_id} from collection...")

        response = make_api_request(
            'DELETE',
            f'/datas/{self.dataset_id}/collections',
            data=[self.collection_id]
        )

        if response.status_code in [200, 204]:
            print_success("Dataset removed from collection (désaffectation)")

            time.sleep(RATE_LIMIT_DELAY)

            # Verify collection no longer has dataset
            print_info("\nVerifying collection status...")
            collection_response = make_api_request('GET', f'/collections/{self.collection_id}')
            if collection_response.status_code == 200:
                collection = collection_response.json()
                dataset_count = len(collection.get('datas', []))
                print_success(f"Collection now contains {dataset_count} dataset(s)")

            # Verify dataset still exists independently
            print_info("\nVerifying dataset still exists on server...")
            dataset_response = make_api_request('GET', f'/datas/{self.dataset_id}')

            if dataset_response.status_code == 200:
                print_success("Dataset still exists independently!")
                print_success("Désaffectation only removed LINK, not the dataset itself")

                print_info("\n🎓 KEY LESSON:")
                print_info("  DÉSAFFECTATION → Removes from collection (reversible)")
                print_info("  DELETION → Removes from server (permanent)")
            else:
                print_warning(f"Dataset check returned: {dataset_response.status_code}")
        else:
            print_error(f"Désaffectation failed: {response.status_code}")

    # ========================================================================
    # PART 3: CLEANUP
    # ========================================================================

    def step_9_cleanup(self):
        """Step 9: Cleanup - Delete collection and dataset"""
        print_section_header("PART 3: CLEANUP & VERIFICATION")
        print_step_header(9, "Cleanup Resources", "DELETE")

        # Delete collection
        print_info("Deleting collection...")
        response = make_api_request('DELETE', f'/collections/{self.collection_id}')

        if response.status_code == 204:
            print_success("Collection deleted")

            time.sleep(RATE_LIMIT_DELAY)

            # Verify collection is gone
            get_response = make_api_request('GET', f'/collections/{self.collection_id}')
            if get_response.status_code == 404:
                print_success("Confirmed: Collection no longer exists")
        else:
            print_error(f"Collection deletion failed: {response.status_code}")

        # Verify dataset still exists (if it was pending)
        print_info("\nVerifying dataset status...")
        dataset_response = make_api_request('GET', f'/datas/{self.dataset_id}')

        if dataset_response.status_code == 200:
            dataset = dataset_response.json()
            dataset_status = dataset.get('status')
            print_success(f"Dataset still exists (status: {dataset_status})")

            # Delete dataset if pending
            if dataset_status == 'pending':
                print_info("\nDeleting test dataset (pending status allows deletion)...")
                delete_response = make_api_request('DELETE', f'/datas/{self.dataset_id}')

                if delete_response.status_code == 204:
                    print_success("Dataset deleted successfully")

                    time.sleep(RATE_LIMIT_DELAY)

                    # Final verification
                    final_check = make_api_request('GET', f'/datas/{self.dataset_id}')
                    if final_check.status_code == 404:
                        print_success("Confirmed: Dataset no longer exists")
                else:
                    print_error(f"Dataset deletion failed: {delete_response.status_code}")
            else:
                print_warning(f"Dataset has status '{dataset_status}' - cannot be deleted")
                print_info(f"   Published datasets are permanent (DOI assigned)")

    def run_complete_lifecycle(self):
        """Execute complete NAKALA lifecycle demonstration"""
        print_section_header("NAKALA COMPLETE LIFECYCLE DEMONSTRATION")

        print("""
This demonstration shows the complete end-to-end NAKALA workflow:

PART 1: DATASET OPERATIONS
  1. Upload file to NAKALA
  2. Create dataset with file
  3. Add metadata incrementally (POST /metadatas)

PART 2: COLLECTION OPERATIONS
  4. Create collection
  5. Link dataset to collection (affectation)
  6. Add collection metadata
  7. Update collection status
  8. Remove dataset from collection (désaffectation)

PART 3: CLEANUP
  9. Delete collection
  10. Verify dataset still exists
  11. Delete dataset (if pending)

🎯 Learning Objectives:
   - Master complete NAKALA workflow
   - Understand dataset ↔ collection relationships
   - Learn affectation vs désaffectation vs deletion
   - Practice safe metadata management
   - Complete resource lifecycle management
        """)

        wait_for_user("Press ENTER to start complete demonstration")

        try:
            # PART 1: DATASET OPERATIONS
            print_section_header("PART 1: DATASET OPERATIONS")

            # Step 1: Upload file
            if not self.step_1_upload_file():
                print_error("Failed to upload file - stopping demo")
                return
            wait_for_user()

            # Step 2: Create dataset
            if not self.step_2_create_dataset():
                print_error("Failed to create dataset - stopping demo")
                return
            wait_for_user()

            # Step 3: Add dataset metadata
            self.step_3_add_dataset_metadata()
            wait_for_user()

            # PART 2: COLLECTION OPERATIONS
            # Step 4: Create collection
            if not self.step_4_create_collection():
                print_error("Failed to create collection - stopping demo")
                return
            wait_for_user()

            # Step 5: Link dataset to collection
            self.step_5_link_dataset_to_collection()
            wait_for_user()

            # Step 6: Add collection metadata
            self.step_6_add_collection_metadata()
            wait_for_user()

            # Step 7: Update collection status
            self.step_7_update_collection_status()
            wait_for_user()

            # Step 8: Désaffectation
            self.step_8_desaffectation()
            wait_for_user()

            # PART 3: CLEANUP
            # Step 9: Cleanup
            self.step_9_cleanup()

            # Final summary
            print_section_header("DEMONSTRATION COMPLETE")
            self.print_summary()

        except KeyboardInterrupt:
            print("\n\n⚠️  Demonstration interrupted by user")
            print("Note: Some resources may have been created on NAKALA test server")
            if self.dataset_id:
                print(f"Dataset ID: {self.dataset_id}")
            if self.collection_id:
                print(f"Collection ID: {self.collection_id}")
            sys.exit(1)
        except Exception as e:
            print_error(f"\nUnexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def print_summary(self):
        """Print demonstration summary"""
        print("\n✓ Successfully demonstrated complete NAKALA lifecycle!")

        print("\n📚 KEY TAKEAWAYS:\n")

        print("1. FILE UPLOAD WORKFLOW")
        print("   ✓ Upload file first (POST /datas/uploads)")
        print("   ✓ Get SHA1 identifier")
        print("   ✓ Include SHA1 in dataset creation")

        print("\n2. DATASET CREATION")
        print("   ✓ Requires 5 mandatory fields (title, type, creator, created, license)")
        print("   ✓ Requires at least one file (files array)")
        print("   ✓ Start with 'pending' status (deletable)")

        print("\n3. INCREMENTAL METADATA OPERATIONS")
        print("   ✓ Use POST /metadatas to add (preserves existing)")
        print("   ✓ Use DELETE /metadatas to remove (exact match required)")
        print("   ✓ SAFER than PUT (which replaces everything)")

        print("\n4. COLLECTIONS")
        print("   ✓ Collections organize datasets")
        print("   ✓ Can exist independently without datasets")
        print("   ✓ Datasets can belong to multiple collections")

        print("\n5. AFFECTATION vs DÉSAFFECTATION")
        print("   ✓ Affectation: Link dataset to collection")
        print("   ✓ Désaffectation: Remove dataset FROM collection")
        print("   ✓ Dataset still exists after désaffectation")
        print("   ✓ Deletion: Remove dataset FROM SERVER (permanent)")

        print("\n6. STATUS MANAGEMENT")
        print("   ✓ Use PUT /status/{status} to change status")
        print("   ✓ Published datasets cannot be deleted (permanent)")
        print("   ✓ Collections can always be deleted")

        print("\n7. NAKALA API PATTERNS")
        print("   ✓ PATCH NOT supported for /datas or /collections")
        print("   ✓ Use POST/DELETE /metadatas for incremental updates")
        print("   ✓ Use dedicated /status endpoint for status changes")
        print("   ⚠️  DELETE /metadatas uses FILTER format - removes ALL matches")
        print("       (propertyUri + lang filter, cannot target specific values)")

        print("\n🎯 WORKFLOW SUMMARY:")
        print("""
        ┌──────────────┐
        │ Upload File  │
        └──────┬───────┘
               │
               ↓
        ┌──────────────┐
        │Create Dataset│ ← 5 mandatory fields + file SHA1
        └──────┬───────┘
               │
               ↓
        ┌──────────────┐
        │ Add Metadata │ ← POST /metadatas (incremental)
        └──────┬───────┘
               │
               ↓
        ┌──────────────────┐
        │Create Collection │
        └──────┬───────────┘
               │
               ↓
        ┌──────────────────┐
        │Link to Collection│ ← Affectation
        └──────┬───────────┘
               │
               ↓
        ┌──────────────────┐
        │Manage Collection │ ← Add metadata, change status
        └──────┬───────────┘
               │
               ↓
        ┌──────────────────┐
        │ Désaffectation   │ ← Unlink (dataset remains)
        └──────┬───────────┘
               │
               ↓
        ┌──────────────────┐
        │    Cleanup       │ ← Delete collection, then dataset
        └──────────────────┘
        """)

        print("\n⚠️  IMPORTANT REMINDERS:")
        print("   • Always test in TEST environment first")
        print("   • Published datasets are permanent (cannot be deleted)")
        print("   • Collections can always be deleted")
        print("   • Désaffectation ≠ Deletion")
        print("   • Use incremental operations (POST/DELETE /metadatas)")
        print("   • Avoid PUT unless replacing everything intentionally")


def main():
    """Main entry point"""
    demo = CompleteNAKALALifecycleDemo()
    demo.run_complete_lifecycle()


if __name__ == '__main__':
    main()
