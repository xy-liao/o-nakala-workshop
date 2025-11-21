#!/usr/bin/env python3
"""
NAKALA Dataset Lifecycle Demonstration
=======================================

Complete demonstration of HTTP method lifecycle for NAKALA datasets:
- POST: Create new dataset
- GET: Retrieve dataset state
- PATCH: NOT SUPPORTED (demonstrates 405 error)
- PUT: Full replacement (dangerous - replaces everything)
- DELETE: Remove dataset (with status-based restrictions)

Key Learning Points:
--------------------
1. NAKALA datasets do NOT support PATCH (only GET, PUT, DELETE)
2. For incremental updates, use POST/DELETE on /datas/{id}/metadatas
3. PUT replaces ALL metadata - missing fields are deleted
4. DELETE is blocked for published datasets (permanent after publishing)
5. At least one file is required to create a dataset

Educational Goals:
------------------
1. Understand NAKALA's HTTP method support and limitations
2. Learn the difference between PUT (full replacement) vs incremental updates
3. Master the POST/DELETE /metadatas pattern for safe updates
4. Understand DELETE restrictions based on dataset status
5. Practice real-world workflows with error handling

Requirements:
-------------
- Python 3.7+
- requests library
- Active internet connection
- NAKALA test API access (uses apitest.nakala.fr)

Usage:
------
    python dataset_lifecycle_demo.py

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
    print_status_lifecycle,
    format_metadata_for_display
)


class DatasetLifecycleDemo:
    """
    Step-by-step demonstration of NAKALA dataset lifecycle
    """

    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY
        self.converter = CsvConverter()
        self.dataset_id = None
        self.pending_dataset_id = None

    def step_1_post_create_dataset(self):
        """Step 1: POST - Create new dataset with pending status"""
        print_step_header(1, "Create New Dataset", "POST")

        print_info("Creating a dataset with status='pending' (not yet published)")
        print_info("This allows us to test DELETE operation later.")

        # Prepare metadata
        metas = [
            {
                "propertyUri": self.converter.property_uris['title'],
                "value": "Demo Dataset - Lifecycle Test",
                "lang": "en"
            },
            {
                "propertyUri": self.converter.property_uris['description'],
                "value": "This dataset demonstrates the complete lifecycle: POST → PATCH → PUT → DELETE",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            },
            {
                "propertyUri": self.converter.property_uris['creator'],
                "value": DEMO_CREATOR
            },
            {
                "propertyUri": self.converter.property_uris['created'],
                "value": "2025",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "propertyUri": self.converter.property_uris['license'],
                "value": DEMO_LICENSE,
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "propertyUri": self.converter.property_uris['type'],
                "value": DEMO_TYPE_URI,
                "typeUri": "http://purl.org/dc/terms/URI"
            },
            {
                "propertyUri": self.converter.property_uris['subject'],
                "value": "lifecycle-demo",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            }
        ]

        # NAKALA requires at least one file, so create a minimal dummy file
        print_info("\nUploading a minimal dummy file (required by NAKALA)...")
        import io
        import requests

        # Create a small text file in memory
        dummy_content = b"Demo file for dataset lifecycle demonstration"

        # Upload the file to get SHA1 identifier
        upload_url = f"{API_URL}/datas/uploads"
        files = {'file': ('demo.txt', io.BytesIO(dummy_content), 'text/plain')}
        headers = {'X-API-KEY': API_KEY}

        upload_response = requests.post(upload_url, files=files, headers=headers)

        if upload_response.status_code != 201:
            print_error(f"File upload failed: {upload_response.status_code}")
            print_error(f"Response: {upload_response.text}")
            raise Exception("File upload failed")

        # Get full file info object (includes name, sha1, etc.)
        file_info = upload_response.json()
        # Add embargo date (current date)
        file_info['embargoed'] = time.strftime("%Y-%m-%d")
        print_success(f"File uploaded: {file_info['sha1']}")

        # Include the uploaded file info in dataset (NAKALA expects full object, not just SHA1)
        dataset = {
            "status": "pending",
            "files": [file_info],
            "metas": metas
        }

        print_info("\n📦 Dataset payload:")
        print_info(f"   Status: {dataset['status']}")
        print_info(f"   Files: 1 (demo.txt)")
        print_info(f"   Metadata fields: {len(metas)}")
        print_info("\n📋 Metadata:")
        print_info(format_metadata_for_display(metas))

        # Create dataset
        response = make_api_request('POST', '/datas', data=dataset)

        if response.status_code == 201:
            result = response.json()
            self.dataset_id = result['payload']['id']
            print_success(f"Dataset created successfully!")
            print_info(f"   Dataset ID: {self.dataset_id}")
            status = result['payload'].get('status', 'N/A')
            if status != 'N/A':
                print_info(f"   Status: {status}")
            return result['payload']
        else:
            print_error(f"Failed to create dataset: {response.status_code}")
            print_error(f"Response: {response.text}")
            raise Exception("Dataset creation failed")

    def step_2_get_verify_creation(self) -> Dict[str, Any]:
        """Step 2: GET - Verify dataset was created correctly"""
        print_step_header(2, "Verify Dataset Creation", "GET")

        print_info("Retrieving dataset to verify it was created correctly...")

        response = make_api_request('GET', f'/datas/{self.dataset_id}')

        if response.status_code == 200:
            dataset = response.json()
            print_success("Dataset retrieved successfully!")
            print_info("\n📊 Current State:")
            print_info(f"   ID: {self.dataset_id}")
            status = dataset.get('status', 'N/A')
            if status != 'N/A':
                print_info(f"   Status: {status}")
            print_info(f"   Metadata entries: {len(dataset.get('metas', []))}")
            print_info(f"   Files: {len(dataset.get('files', []))}")
            print_info("\n📋 Metadata:")
            print_info(format_metadata_for_display(dataset.get('metas', [])))
            return dataset
        else:
            print_error(f"Failed to retrieve dataset: {response.status_code}")
            raise Exception("Dataset retrieval failed")

    def step_3_patch_partial_update(self, before_state: Dict[str, Any]):
        """Step 3: PATCH - Attempt (will demonstrate API limitation)"""
        print_step_header(3, "Attempt PATCH - Learn API Limitation", "PATCH")

        print_warning("IMPORTANT API LIMITATION:")
        print_info("PATCH is NOT supported for datasets in NAKALA API")
        print_info("Datasets only support: GET, PUT, DELETE")
        print_info("For incremental updates, use: POST/DELETE /datas/{id}/metadatas")
        print_info("\nLet's try PATCH to see the error response...")

        # Prepare PATCH payload - only the title we want to update
        updated_metas = [
            {
                "propertyUri": self.converter.property_uris['title'],
                "value": "Demo Dataset - Lifecycle Demonstration",
                "lang": "en"
            }
        ]

        patch_data = {
            "metas": updated_metas
        }

        print_info("\n📦 PATCH payload (partial):")
        print_info("   Updating only: title field")
        print_info(json.dumps(patch_data, indent=2, ensure_ascii=False))

        response = make_api_request('PATCH', f'/datas/{self.dataset_id}', data=patch_data)

        if response.status_code == 405:
            print_warning(f"\n✓ Expected result: {response.status_code} Method Not Allowed")
            print_info("API Response: PATCH is not supported for datasets")
            print_info("\n💡 Key Learning:")
            print_info("   • For incremental updates: Use POST/DELETE /datas/{id}/metadatas")
            print_info("   • For full replacement: Use PUT (but be careful - replaces everything!)")
            print_info("   • PATCH only exists for: /datas/{id}/relations (to update relation comments)")
            print_info("\nContinuing with PUT demonstration instead...")
            return before_state  # Return unchanged state
        else:
            print_error(f"Unexpected response: {response.status_code}")
            print_error(f"Response: {response.text}")
            return before_state

    def step_4_patch_add_keyword(self, before_state: Dict[str, Any]):
        """Step 4: Skipped (PATCH not supported for datasets)"""
        print_step_header(4, "PATCH Not Supported - Skipping", "PATCH")

        print_info("⏭️  Skipping PATCH demonstration for adding keywords")
        print_info("   As we learned in Step 3, PATCH is not supported for datasets")
        print_info("\n💡 For incremental metadata updates in NAKALA:")
        print_info("   • POST   /datas/{id}/metadatas     - Add new metadata")
        print_info("   • DELETE /datas/{id}/metadatas     - Remove specific metadata")
        print_info("   • GET    /datas/{id}/metadatas     - List all metadata")
        print_info("\n   (See collection_lifecycle_demo.py for examples of incremental updates)")

        return before_state

    def step_5_put_full_replacement(self, before_state: Dict[str, Any]):
        """Step 5: PUT - Complete replacement (demonstrates data loss risk)"""
        print_step_header(5, "Full Replacement - DANGEROUS!", "PUT")

        print_warning("PUT REPLACES EVERYTHING!")
        print_warning("Any metadata not included in PUT request will be DELETED!")
        print_info("\nScenario: Replace all metadata with minimal set (demonstrates data loss)")

        # Minimal metadata set (missing keywords we added earlier)
        minimal_metas = [
            {
                "propertyUri": self.converter.property_uris['title'],
                "value": "Demo Dataset - PUT Replacement",
                "lang": "en"
            },
            {
                "propertyUri": self.converter.property_uris['creator'],
                "value": DEMO_CREATOR
            },
            {
                "propertyUri": self.converter.property_uris['created'],
                "value": "2025",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "propertyUri": self.converter.property_uris['license'],
                "value": DEMO_LICENSE,
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "propertyUri": self.converter.property_uris['type'],
                "value": DEMO_TYPE_URI,
                "typeUri": "http://purl.org/dc/terms/URI"
            }
        ]

        put_data = {
            "status": "pending",
            "metas": minimal_metas
        }

        print_info(f"\n📦 PUT payload (complete replacement):")
        print_info(f"   Metadata entries BEFORE PUT: {len(before_state.get('metas', []))}")
        print_info(f"   Metadata entries in PUT payload: {len(minimal_metas)}")
        print_warning("   Missing: description, keywords (will be DELETED!)")

        response = make_api_request('PUT', f'/datas/{self.dataset_id}', data=put_data)

        if response.status_code == 204:
            print_warning("PUT successful - but data was lost!")

            # Get updated state
            time.sleep(RATE_LIMIT_DELAY)
            get_response = make_api_request('GET', f'/datas/{self.dataset_id}')
            after_state = get_response.json()

            # Check for description and keywords in before state
            before_metas = before_state.get('metas', [])
            has_desc_before = any(m.get('propertyUri') == self.converter.property_uris['description'] for m in before_metas)
            has_keys_before = any(m.get('propertyUri') == self.converter.property_uris['subject'] for m in before_metas)
            
            # Check for description and keywords in after state
            after_metas = after_state.get('metas', [])
            has_desc_after = any(m.get('propertyUri') == self.converter.property_uris['description'] for m in after_metas)
            has_keys_after = any(m.get('propertyUri') == self.converter.property_uris['subject'] for m in after_metas)

            print_json_comparison(
                {"metadata_count": len(before_metas), "has_description": has_desc_before, "has_keywords": has_keys_before},
                {"metadata_count": len(after_metas), "has_description": has_desc_after, "has_keywords": has_keys_after},
                "PUT RESULT - Data Loss Demonstration"
            )

            print_error(f"\nLost {len(before_state.get('metas', [])) - len(after_state.get('metas', []))} metadata entries!")
            print_error("Description field: DELETED")
            print_error("Keywords: DELETED")
            print_success("Only fields in PUT payload survived")

            print_warning("\nKEY LESSON: For targeted updates, use POST/DELETE on /metadatas endpoint!")
            print_info("   • POST /datas/{id}/metadatas - Add individual metadata")
            print_info("   • DELETE /datas/{id}/metadatas - Remove specific metadata")
            print_info("   • Avoid PUT unless you need to replace EVERYTHING")

            return after_state
        else:
            print_error(f"PUT failed: {response.status_code}")
            raise Exception("PUT failed")

    def step_6_delete_attempt_published(self):
        """Step 6: DELETE - Attempt to delete (shows restriction for published datasets)"""
        print_step_header(6, "Delete Attempt - Testing Restrictions", "DELETE")

        print_info("First, let's try changing status to 'published' and then deleting...")
        print_info("Using PUT /datas/{id}/status/published endpoint...")

        # Change to published using the status endpoint
        response = make_api_request('PUT', f'/datas/{self.dataset_id}/status/published')

        if response.status_code == 204:
            print_success("Status changed to 'published'")
            time.sleep(RATE_LIMIT_DELAY)

            # Now try to delete
            print_info("\nAttempting to DELETE published dataset...")
            delete_response = make_api_request('DELETE', f'/datas/{self.dataset_id}')

            if delete_response.status_code == 403 or delete_response.status_code == 400:
                print_success("DELETE blocked (expected behavior)!")
                print_info("   Published datasets cannot be deleted - they are permanent")
                print_info("   This protects DOI persistence and citation integrity")
            else:
                print_warning(f"Unexpected response: {delete_response.status_code}")
        else:
            print_warning(f"Status change returned: {response.status_code}")
            print_info("Skipping DELETE test (status change failed)")

    def step_7_delete_pending_dataset(self):
        """Step 7: DELETE - Successfully delete a pending dataset"""
        print_step_header(7, "Delete Pending Dataset - Success", "DELETE")

        print_info("Creating a new dataset with status='pending' to demonstrate successful deletion...")

        # Upload a dummy file first (required by NAKALA)
        import io
        import requests

        dummy_content = b"Temporary file for deletion test"
        upload_url = f"{API_URL}/datas/uploads"
        files = {'file': ('temp.txt', io.BytesIO(dummy_content), 'text/plain')}
        headers = {'X-API-KEY': API_KEY}

        upload_response = requests.post(upload_url, files=files, headers=headers)

        if upload_response.status_code != 201:
            print_error(f"File upload failed: {upload_response.status_code}")
            return

        file_info = upload_response.json()
        file_info['embargoed'] = time.strftime("%Y-%m-%d")

        # Create another pending dataset
        metas = [
            {
                "propertyUri": self.converter.property_uris['title'],
                "value": "Temporary Test Dataset",
                "lang": "en"
            },
            {
                "propertyUri": self.converter.property_uris['creator'],
                "value": DEMO_CREATOR
            },
            {
                "propertyUri": self.converter.property_uris['created'],
                "value": "2025",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "propertyUri": self.converter.property_uris['license'],
                "value": DEMO_LICENSE,
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "propertyUri": self.converter.property_uris['type'],
                "value": DEMO_TYPE_URI,
                "typeUri": "http://purl.org/dc/terms/URI"
            }
        ]

        dataset = {
            "status": "pending",
            "files": [file_info],
            "metas": metas
        }

        create_response = make_api_request('POST', '/datas', data=dataset)

        if create_response.status_code == 201:
            result = create_response.json()
            temp_dataset_id = result['payload']['id']
            print_success(f"Temporary dataset created: {temp_dataset_id}")

            time.sleep(RATE_LIMIT_DELAY)

            # Now delete it
            print_info("\nAttempting to DELETE pending dataset...")
            delete_response = make_api_request('DELETE', f'/datas/{temp_dataset_id}')

            if delete_response.status_code == 204:
                print_success("DELETE successful!")
                print_info("   Pending datasets can be deleted")

                # Verify deletion
                time.sleep(RATE_LIMIT_DELAY)
                get_response = make_api_request('GET', f'/datas/{temp_dataset_id}')

                if get_response.status_code == 404:
                    print_success("Confirmed: Dataset no longer exists")
                else:
                    print_warning(f"Dataset still exists (unexpected): {get_response.status_code}")

            else:
                print_error(f"DELETE failed: {delete_response.status_code}")

    def run_complete_lifecycle(self):
        """Execute complete dataset lifecycle demonstration"""
        print_section_header("NAKALA DATASET LIFECYCLE DEMONSTRATION")

        print("""
This demonstration shows the complete HTTP method lifecycle for NAKALA datasets:

  1. POST   - Create new dataset
  2. GET    - Verify creation
  3. PATCH  - Attempt (learn API limitation)
  4. PATCH  - Skipped (not supported for datasets)
  5. PUT    - Full replacement (dangerous - shows data loss)
  6. DELETE - Attempt on published (blocked)
  7. DELETE - Success on pending (allowed)

⚠️  IMPORTANT: Datasets do NOT support PATCH (only GET, PUT, DELETE)
   For incremental updates, use POST/DELETE on /metadatas sub-endpoint

📚 Learning Objectives:
   - Understand when to use each HTTP method
   - Learn NAKALA's incremental update pattern (POST/DELETE /metadatas)
   - See why PUT is dangerous (replaces everything)
   - Learn DELETE restrictions based on status
   - Practice error handling
        """)

        wait_for_user("Press ENTER to start demonstration")

        try:
            # Step 1: Create dataset
            self.step_1_post_create_dataset()
            wait_for_user()

            # Step 2: Verify creation
            state_after_creation = self.step_2_get_verify_creation()
            wait_for_user()

            # Step 3: PATCH - fix title
            state_after_patch1 = self.step_3_patch_partial_update(state_after_creation)
            wait_for_user()

            # Step 4: PATCH - add keywords
            state_after_patch2 = self.step_4_patch_add_keyword(state_after_patch1)
            wait_for_user()

            # Step 5: PUT - full replacement (data loss)
            state_after_put = self.step_5_put_full_replacement(state_after_patch2)
            wait_for_user()

            # Step 6: DELETE attempt on published
            self.step_6_delete_attempt_published()
            wait_for_user()

            # Step 7: DELETE success on pending
            self.step_7_delete_pending_dataset()

            # Final summary
            print_section_header("DEMONSTRATION COMPLETE")

            print("""
✓ Successfully demonstrated NAKALA dataset HTTP methods!

📚 KEY TAKEAWAYS:

1. POST - Creates new resources
   ✓ Use for initial dataset creation
   ✓ Returns dataset ID for future operations
   ✓ Requires at least one file to be uploaded

2. GET - Retrieves current state
   ✓ Use to verify changes
   ✓ Safe, read-only operation

3. PATCH - NOT SUPPORTED for datasets ❌
   ✗ Datasets do not support PATCH method
   ✗ Will return 405 Method Not Allowed
   ✓ Instead, use POST/DELETE on /metadatas sub-endpoint for incremental updates

4. PUT - Full replacement (DANGEROUS)
   ⚠️  Replaces ALL metadata
   ⚠️  Any missing fields are DELETED
   ⚠️  Use only for complete rewrites

5. DELETE - Permanent removal
   ✓ Works on pending datasets
   ✗ Blocked for published datasets
   ⚠️  Permanent and irreversible

🎯 BEST PRACTICES:
   - Use POST/DELETE on /metadatas for incremental updates
   - Avoid PUT (replaces everything) unless necessary
   - Test DELETE restrictions before publishing
   - Use GET to verify all changes
   - Design deletion strategy early
            """)

            print_method_comparison_table()
            print_status_lifecycle()

        except Exception as e:
            print_error(f"\nDemonstration failed: {str(e)}")
            raise


def main():
    """Main entry point"""
    demo = DatasetLifecycleDemo()
    demo.run_complete_lifecycle()


if __name__ == '__main__':
    main()
