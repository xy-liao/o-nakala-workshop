#!/usr/bin/env python3
"""
NAKALA Rights Management Demonstration
=======================================

Demonstrates NAKALA Workflow 3: Rights and Access Control

This demo covers collaborative access management in NAKALA:
- Understanding rights roles hierarchy
- Assigning permissions to datasets and collections
- Verifying access rights
- Group management concepts

NAKALA Rights Roles:
--------------------
- ROLE_OWNER: Full control (automatic, cannot be removed)
- ROLE_ADMIN: Can manage rights, modify content, status changes
- ROLE_MODERATOR: Content moderation (official role, see apitest-nakala.json:802)
- ROLE_EDITOR: Can modify metadata and content
- ROLE_READER: Read-only access to published data
- ROLE_DEPOSITOR: Attribution only (automatic for creator, no direct rights)

Key Learning Points:
--------------------
1. ROLE_OWNER is automatic for dataset creator
2. Rights can be assigned to individual users or groups
3. Rights hierarchy determines capabilities
4. Collection rights are independent from dataset rights
5. Only OWNER can delete resources

Educational Goals:
------------------
1. Understand NAKALA rights hierarchy
2. Learn rights assignment workflow
3. Practice access control verification
4. Understand group-based permissions
5. Master collaborative dataset management

Note on Test Environment:
-------------------------
The NAKALA test API has limitations for rights management:
- Group creation may require additional permissions
- User search may return limited results
- Some operations may fail due to test environment restrictions

This demo focuses on educational concepts and shows the correct
API patterns, even if some operations cannot complete in test environment.

Requirements:
-------------
- Python 3.7+
- requests library
- Active internet connection
- NAKALA test API access (uses apitest.nakala.fr)

Usage:
------
    python rights_management_demo.py

Author: Syl (NAKALA API Educational Resources)
Created: November 17, 2025
License: CC0-1.0


Note: Part of user-created pedagogical suite, not official Huma-Num documentation.
      Implements Workflow 3 from NAKALA_API_VISUAL_GUIDE.md
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

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
    PROPERTY_URIS
)

# Known test users for fallback when search fails (e.g. empty server)
KNOWN_TEST_USERS = {
    "tnakala": "5a38883d-6b58-450a-9892-0545b7461973",
    "unakala1": "33170cfe-f53c-550b-5fb6-4814ce981293"  # Just the UUID, no key!
}

from nakala.demo_helpers import (
    make_api_request,
    print_section_header,
    print_step_header,
    print_success,
    print_warning,
    print_error,
    print_info,
    wait_for_user
)


class RightsManagementDemo:
    """
    Demonstrate NAKALA rights and access control
    """

    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY
        self.dataset_id = None
        self.collection_id = None

    def create_test_dataset(self) -> str:
        """Create a test dataset for rights demonstration"""
        print_info("Creating test dataset...")

        # IMPORTANT: Datasets require at least one file
        # Step 1: Upload a dummy file
        print_info("  Step 1: Uploading dummy file...")
        import io
        import requests

        dummy_content = b"Rights Management Demo - Test File\nThis is a demonstration file for rights management."
        files = {'file': ('rights_demo.txt', io.BytesIO(dummy_content), 'text/plain')}

        upload_response = requests.post(
            f'{self.api_url}/datas/uploads',
            headers={'X-API-KEY': self.api_key},
            files=files
        )

        if upload_response.status_code != 201:
            raise Exception(f"File upload failed: {upload_response.status_code}")

        # Get full file info object (includes name, sha1, etc.)
        file_info = upload_response.json()
        print_success(f"  File uploaded: {file_info['sha1']}")

        # Step 2: Create dataset with metadata and file reference
        print_info("  Step 2: Creating dataset with metadata...")

        metas = [
            {
                "propertyUri": PROPERTY_URIS['title'],
                "value": "Rights Management Test Dataset",
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['description'],
                "value": "Dataset for demonstrating collaborative access control",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['type'],
                "value": DEMO_TYPE_URI,
                "typeUri": "http://www.w3.org/2001/XMLSchema#anyURI"
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

        dataset = {
            "status": "pending",
            "metas": metas,
            "files": [file_info]  # Include full file info object
        }

        response = make_api_request('POST', '/datas', data=dataset)

        if response.status_code == 201:
            result = response.json()
            dataset_id = result['payload']['id']
            print_success(f"Test dataset created: {dataset_id}")
            return dataset_id
        else:
            raise Exception(f"Failed to create dataset: {response.status_code}")

    def demonstrate_rights_hierarchy(self):
        """Explain NAKALA rights hierarchy"""
        print_section_header("NAKALA RIGHTS HIERARCHY")

        print("""
NAKALA supports 5 rights roles with different capabilities:

╔═══════════════════════════════════════════════════════════════════════════╗
║                        RIGHTS ROLES HIERARCHY                              ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  1. ROLE_OWNER (Highest)                                                   ║
║     ✓ Full control over resource                                           ║
║     ✓ Can delete resource                                                  ║
║     ✓ Can modify status (publish/unpublish)                                ║
║     ✓ Can assign/modify all rights                                         ║
║     ✓ Can modify metadata and files                                        ║
║     • Automatic for dataset creator                                        ║
║     • Cannot be removed or changed                                         ║
║                                                                            ║
║  2. ROLE_ADMIN                                                             ║
║     ✓ Can manage rights (assign EDITOR/READER)                             ║
║     ✓ Can modify metadata and files                                        ║
║     ✓ Can modify status                                                    ║
║     ✗ Cannot delete resource (⚠️  ambiguous in official docs)              ║
║     • Good for project managers                                            ║
║                                                                            ║
║  3. ROLE_MODERATOR                                                         ║
║     ✓ Content moderation capability                                        ║
║     ✓ Can moderate published data                                          ║
║     ✗ Cannot manage rights                                                 ║
║     • Official role (apitest-nakala.json:802, 841, 2935)                   ║
║     • "modération de la donnée"                                            ║
║                                                                            ║
║  4. ROLE_EDITOR                                                            ║
║     ✓ Can modify metadata and content                                      ║
║     ✓ Can add/modify files                                                 ║
║     ✗ Cannot modify status                                                 ║
║     ✗ Cannot manage rights                                                 ║
║     ✗ Cannot delete resource                                               ║
║     • Good for collaborators                                               ║
║                                                                            ║
║  5. ROLE_READER                                                            ║
║     ✓ Can view published data                                              ║
║     ✗ Cannot modify anything                                               ║
║     ✗ Cannot view pending data                                             ║
║     • Good for reviewers                                                   ║
║                                                                            ║
║  6. ROLE_DEPOSITOR (Attribution Role)                                      ║
║     • Automatic for creator (alongside ROLE_OWNER)                         ║
║     • No direct rights granted                                             ║
║     • Used for attribution/tracking only                                   ║
║     • Official source: apitest-nakala.json:841                             ║
║                                                                            ║
║  📊 Hierarchy: OWNER > ADMIN > MODERATOR > EDITOR > READER                 ║
║     (DEPOSITOR = attribution only, no hierarchy position)                  ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

Capability Matrix:
──────────────────

                    OWNER    ADMIN   MODERATOR   EDITOR   READER   DEPOSITOR
──────────────────────────────────────────────────────────────────────────────
View Resource         ✓       ✓         ✓         ✓        ✓         ✗
Modify Metadata       ✓       ✓         ✓         ✓        ✗         ✗
Modify Files          ✓       ✓         ✓         ✓        ✗         ✗
Modify Status         ✓       ✓         ✗         ✗        ✗         ✗
Manage Rights         ✓       ✓         ✗         ✗        ✗         ✗
Moderate Content      ✓       ✓         ✓         ✗        ✗         ✗
Delete Resource       ✓       ✗         ✗         ✗        ✗         ✗
──────────────────────────────────────────────────────────────────────────────
        """)

        wait_for_user("Press ENTER to continue")

    def demonstrate_automatic_owner(self):
        """Show that creator automatically becomes OWNER"""
        print_section_header("AUTOMATIC OWNER ROLE")

        print("""
When you create a dataset or collection, you automatically become the OWNER.
Let's create a dataset and verify the automatic OWNER role.
        """)

        wait_for_user("Press ENTER to create dataset and check rights")

        # Create dataset
        self.dataset_id = self.create_test_dataset()
        time.sleep(RATE_LIMIT_DELAY)

        print_step_header("1", "Retrieve dataset rights", "GET")

        response = make_api_request('GET', f'/datas/{self.dataset_id}/rights')

        if response.status_code == 200:
            rights = response.json()

            print_info("\n📊 Current Rights:")
            print_info(json.dumps(rights, indent=2))

            print_success("\nCreator automatically has ROLE_OWNER")
            print_success("ROLE_DEPOSITOR also assigned automatically")
            print_info("\nKey observations:")
            print_info("  • ROLE_OWNER: Full control (automatic)")
            print_info("  • ROLE_DEPOSITOR: Attribution only (automatic)")
            print_info("  • Both roles cannot be removed")
        else:
            print_error(f"Failed to retrieve rights: {response.status_code}")
            print_error(response.text)

    def demonstrate_group_creation_concept(self):
        """Explain group creation concept (may not work in test API)"""
        print_section_header("USER GROUP MANAGEMENT")

        print("""
NAKALA supports user groups for collaborative access management.

╔═══════════════════════════════════════════════════════════════════════════╗
║                        USER GROUP WORKFLOW                                 ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  STEP 1: Create Group                                                      ║
║  ────────────────────                                                      ║
║                                                                            ║
║  Endpoint: POST /groups                                                    ║
║                                                                            ║
║  Body:                                                                     ║
║  {                                                                         ║
║    "name": "Research Team A",                                              ║
║    "users": [                                                              ║
║      {"username": "user1", "role": "ROLE_ADMIN"},                          ║
║      {"username": "user2", "role": "ROLE_USER"}                            ║
║    ]                                                                       ║
║  }                                                                         ║
║                                                                            ║
║  Response: HTTP 201 + Group ID                                             ║
║                                                                            ║
║  ────────────────────────────────────────────────────────────────────────  ║
║                                                                            ║
║  STEP 2: Find Group ID                                                     ║
║  ──────────────────                                                        ║
║                                                                            ║
║  Endpoint: GET /groups/search?q=Research Team A&limit=1                    ║
║                                                                            ║
║  Response: [{"id": "group-uuid", "name": "Research Team A", ...}]          ║
║                                                                            ║
║  ────────────────────────────────────────────────────────────────────────  ║
║                                                                            ║
║  STEP 3: Assign Group Rights to Dataset                                    ║
║  ───────────────────────────────────                                       ║
║                                                                            ║
║  Endpoint: POST /datas/{dataset-id}/rights                                 ║
║                                                                            ║
║  Body:                                                                     ║
║  [                                                                         ║
║    {                                                                       ║
║      "id": "group-uuid",                                                   ║
║      "role": "ROLE_EDITOR"                                                 ║
║    }                                                                       ║
║  ]                                                                         ║
║                                                                            ║
║  Response: HTTP 201/204 (Success)                                          ║
║                                                                            ║
║  ────────────────────────────────────────────────────────────────────────  ║
║                                                                            ║
║  STEP 4: Verify Rights                                                     ║
║  ──────────────────                                                        ║
║                                                                            ║
║  Endpoint: GET /datas/{dataset-id}/rights                                  ║
║                                                                            ║
║  Response: All users in group now have EDITOR rights to dataset            ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

Benefits of Groups:
───────────────────
✓ Manage multiple users at once
✓ Assign rights to entire team
✓ Easy to add/remove team members
✓ Consistent permissions across resources
✓ Ideal for research projects

Important: Groups must have at least one user besides yourself.
           Your account is automatically added as ROLE_OWNER.
           For this demo, we'll use the test user 'tnakala'.
        """)

        wait_for_user("Press ENTER to create a test group with validation")

        print_step_header("1", "Create test group with valid user", "POST")

        group_data = {
            "name": "NAKALA Demo Test Group",
            "users": [
                {
                    "username": "tnakala",  # Test user available in test API
                    "role": "ROLE_USER"
                }
            ]
        }

        print_info("\n📦 POST /groups payload:")
        print_info(json.dumps(group_data, indent=2))

        response = make_api_request('POST', '/groups', data=group_data)

        if response.status_code in [200, 201]:
            result = response.json()
            print_success(f"\n✓ Group created successfully!")
            print_info(json.dumps(result, indent=2))

            # Retrieve and display group details
            group_id = result.get('payload', {}).get('id')
            if group_id:
                print_info("\n🔍 Retrieving group details...")
                group_response = make_api_request('GET', f'/groups/{group_id}')
                if group_response.status_code == 200:
                    group_info = group_response.json()
                    print_info("\n📊 Group Members:")
                    for user in group_info.get('users', []):
                        username = user.get('username', 'Unknown')
                        role = user.get('role', 'Unknown')
                        fullname = user.get('fullname', 'Unknown')
                        print_info(f"  • {username} ({fullname}) → {role}")

                    print_success("\n✓ Note: Your account was automatically added as ROLE_OWNER")

                    # Step 2: Assign group rights to dataset
                    if self.dataset_id:
                        wait_for_user("\nPress ENTER to assign group rights to the test dataset")

                        print_step_header("2", "Assign group rights to dataset", "POST")

                        rights_data = [
                            {
                                "id": group_id,  # Group UUID
                                "role": "ROLE_EDITOR"
                            }
                        ]

                        print_info("\n📦 POST /datas/{id}/rights payload:")
                        print_info(json.dumps(rights_data, indent=2))

                        assign_response = make_api_request('POST', f'/datas/{self.dataset_id}/rights', data=rights_data)

                        if assign_response.status_code == 200:
                            print_success("\n✓ Group rights assigned successfully!")

                            # Verify rights were added
                            print_step_header("3", "Verify rights assignment", "GET")

                            verify_response = make_api_request('GET', f'/datas/{self.dataset_id}/rights')
                            if verify_response.status_code == 200:
                                all_rights = verify_response.json()
                                print_success(f"\n✓ Total rights: {len(all_rights)}")
                                print_info("\n📊 All Rights on Dataset:")
                                for right in all_rights:
                                    name = right.get('name', 'Unknown')
                                    right_type = right.get('type', 'Unknown')
                                    role = right.get('role', 'Unknown')
                                    print_info(f"  • {name} ({right_type}) → {role}")

                                print_success("\n✓ Group rights assignment complete!")
                                print_info("   All users in the group now have EDITOR access to this dataset")
                        else:
                            print_error(f"\n✗ Rights assignment failed: {assign_response.status_code}")
                            print_error(assign_response.text)

                    # Cleanup test group
                    print_info("\n🧹 Cleaning up test group...")
                    delete_response = make_api_request('DELETE', f'/groups/{group_id}')
                    if delete_response.status_code == 200:
                        print_success("Test group deleted")
                        print_info("   Note: Group rights on dataset are automatically removed")
        else:
            print_error(f"\n✗ Group creation failed: {response.status_code}")
            try:
                error_data = response.json()
                print_error(f"Response: {json.dumps(error_data, indent=2)}")

                # Explain common validation errors
                if response.status_code == 422:
                    print_warning("\n⚠️  Validation Error - Common Causes:")
                    print_info("  • Groups must have at least one user besides yourself")
                    print_info("  • Username must be valid (use GET /users/search)")
                    print_info("  • Your account is automatically added as ROLE_OWNER")
                elif response.status_code == 404:
                    print_warning("\n⚠️  User Not Found:")
                    print_info("  • The username specified doesn't exist")
                    print_info("  • Use GET /users/search to find valid usernames")
            except:
                print_error(f"Response text: {response.text}")

    def demonstrate_individual_rights_assignment(self):
        """Demonstrate assigning rights to individual users"""
        print_section_header("INDIVIDUAL USER RIGHTS ASSIGNMENT")

        print("""
Rights can be assigned to individual users without creating a group.
The workflow is identical to group rights assignment.

Prerequisite: User UUID
───────────────────────
The NAKALA API requires user UUIDs (not usernames) for rights assignment.
You can find a user's UUID by searching for them.

Use Cases:
──────────
✓ Quick collaboration with one person
✓ Guest access for reviewers
✓ Temporary access for external collaborators
        """)

        if not self.dataset_id:
            print_warning("\nNo dataset available. Skipping rights assignment demo.")
            return

        wait_for_user("\nPress ENTER to search for a user and assign rights")

        # Step 1: Find user UUID via search
        target_username = "tnakala"  # Using 'tnakala' as it is a known test user
        print_step_header("1", f"Find UUID for user '{target_username}'", "GET")

        print_info(f"Searching for user '{target_username}'...")
        
        target_uuid = None
        target_fullname = "Unknown"

        try:
            response = make_api_request('GET', f'/users/search?q={target_username}&limit=1')
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    user_data = results[0]
                    target_uuid = user_data.get('id')
                    target_fullname = user_data.get('fullName') or user_data.get('fullname', 'Unknown')
                    
                    print_success(f"✓ User found: {target_fullname} (@{target_username})")
                    print_info(f"   UUID: {target_uuid}")
                else:
                    print_warning(f"User '{target_username}' not found in search results.")
            else:
                print_warning(f"Search failed: {response.status_code}")
        except Exception as e:
            print_warning(f"Search request failed: {e}")

        # Fallback logic if search failed or returned no results
        if not target_uuid:
            if target_username in KNOWN_TEST_USERS:
                target_uuid = KNOWN_TEST_USERS[target_username]
                target_fullname = f"Test User ({target_username})"
                print_warning(f"\n⚠️  Search failed (possibly empty test server).")
                print_info(f"   Using known fallback UUID for '{target_username}' to continue demo.")
                print_info(f"   UUID: {target_uuid}")
            else:
                print_error(f"Cannot proceed with rights assignment without a valid user UUID.")
                return

        # Step 2: Assign individual user rights
        wait_for_user(f"\nPress ENTER to assign READER rights to {target_fullname}")

        print_step_header("2", "Assign individual user rights", "POST")

        rights_data = [
            {
                "id": target_uuid,
                "role": "ROLE_READER"
            }
        ]

        print_info("\n📦 POST /datas/{id}/rights payload:")
        print_info(json.dumps(rights_data, indent=2))

        assign_response = make_api_request('POST', f'/datas/{self.dataset_id}/rights', data=rights_data)

        if assign_response.status_code == 200:
            print_success("\n✓ Individual user rights assigned successfully!")

            # Step 3: Verify assignment
            print_step_header("3", "Verify individual rights assignment", "GET")

            verify_response = make_api_request('GET', f'/datas/{self.dataset_id}/rights')
            if verify_response.status_code == 200:
                all_rights = verify_response.json()
                print_success(f"\n✓ Total rights: {len(all_rights)}")
                print_info("\n📊 All Rights on Dataset:")
                for right in all_rights:
                    name = right.get('name', 'Unknown')
                    right_type = right.get('type', 'Unknown')
                    role = right.get('role', 'Unknown')
                    username = right.get('username', '')
                    
                    # Highlight our target user
                    prefix = "  ➤" if username == target_username else "  •"
                    
                    if username:
                        print_info(f"{prefix} {name} (@{username}, {right_type}) → {role}")
                    else:
                        print_info(f"{prefix} {name} ({right_type}) → {role}")

                print_success(f"\n✓ Individual user rights assignment complete!")
        else:
            print_error(f"\n✗ Rights assignment failed: {assign_response.status_code}")
            print_error(assign_response.text)

    def demonstrate_rights_verification(self):
        """Demonstrate how to verify current rights"""
        print_section_header("RIGHTS VERIFICATION")

        print("""
It's important to verify rights after assignment to ensure correct access.

Verification Workflow:
──────────────────────

1. GET /datas/{id}/rights → Retrieve all assigned rights
2. Parse response to identify roles
3. Verify expected users/groups have correct roles
4. Check for any unexpected permissions
        """)

        if not self.dataset_id:
            print_warning("\nNo dataset available. Skipping verification demo.")
            return

        wait_for_user("\nPress ENTER to verify current rights")

        print_step_header("1", "Verify dataset rights", "GET")

        response = make_api_request('GET', f'/datas/{self.dataset_id}/rights')

        if response.status_code == 200:
            rights = response.json()

            print_success("\n✓ Rights retrieved successfully")
            print_info("\n📊 Current Rights Assignment:")
            print_info(json.dumps(rights, indent=2))

            # Analyze rights
            print_info("\n🔍 Rights Analysis:")
            for right in rights:
                role = right.get('role', 'Unknown')
                right_type = right.get('type', 'Unknown')
                right_id = right.get('id', 'Unknown')
                print_info(f"  • {role} → {right_type} (ID: {right_id})")

            print_success("\n✓ Verification complete")
        else:
            print_error(f"Failed to retrieve rights: {response.status_code}")

    def demonstrate_collection_rights(self):
        """Explain collection rights concepts"""
        print_section_header("COLLECTION RIGHTS MANAGEMENT")

        print("""
Collections can have rights assigned just like datasets.

╔═══════════════════════════════════════════════════════════════════════════╗
║                      COLLECTION RIGHTS WORKFLOW                            ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Same Pattern as Datasets:                                                 ║
║                                                                            ║
║  1. Create Collection                                                      ║
║     POST /collections                                                      ║
║     → Creator becomes ROLE_OWNER automatically                             ║
║                                                                            ║
║  2. Assign Rights                                                          ║
║     POST /collections/{id}/rights                                          ║
║     Body: [{"id": "user-or-group-id", "role": "ROLE_EDITOR"}]              ║
║                                                                            ║
║  3. Verify Rights                                                          ║
║     GET /collections/{id}/rights                                           ║
║                                                                            ║
║  Important Distinction:                                                    ║
║  ────────────────────                                                      ║
║                                                                            ║
║  • Collection rights ≠ Dataset rights                                      ║
║  • Rights are independent                                                  ║
║  • Access to collection does NOT grant access to datasets                  ║
║  • Must assign rights separately to each resource                          ║
║                                                                            ║
║  Use Case:                                                                 ║
║  ─────────                                                                 ║
║                                                                            ║
║  1. Grant EDITOR to collection → Can organize datasets                     ║
║  2. Grant READER to datasets → Can view but not modify                     ║
║                                                                            ║
║  Result: User can curate collection but only read datasets                 ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def cleanup(self):
        """Cleanup test resources"""
        print_section_header("CLEANUP")

        print_info("Cleaning up test resources...")

        if self.dataset_id:
            response = make_api_request('DELETE', f'/datas/{self.dataset_id}')
            if response.status_code in [200, 204]:
                print_success(f"✓ Dataset deleted: {self.dataset_id}")
            else:
                print_warning(f"⚠️  Dataset deletion failed (may already be deleted)")

        if self.collection_id:
            response = make_api_request('DELETE', f'/collections/{self.collection_id}')
            if response.status_code in [200, 204]:
                print_success(f"✓ Collection deleted: {self.collection_id}")
            else:
                print_warning(f"⚠️  Collection deletion failed (may already be deleted)")

        print_success("\nCleanup complete!")

    def run_demo(self):
        """Run all demonstration scenarios"""
        print_section_header("NAKALA RIGHTS MANAGEMENT DEMO")

        print("""
Welcome to the Rights Management Demonstration!
================================================

This demo covers NAKALA Workflow 3: Rights and Access Control

We'll explore:
1. Rights hierarchy and roles
2. Automatic OWNER role assignment
3. Group-based permissions concepts
4. Individual user rights assignment
5. Rights verification workflow
6. Collection rights management

Note: Some operations may not complete in test environment due to:
- Limited user account access
- Restricted group creation permissions
- Test API environment limitations

The demo focuses on teaching correct API patterns and concepts.
        """)

        wait_for_user("Press ENTER to start demonstration")

        try:
            # Part 1: Rights hierarchy
            self.demonstrate_rights_hierarchy()
            wait_for_user("\n\nPress ENTER to continue to Part 2")

            # Part 2: Automatic owner
            self.demonstrate_automatic_owner()
            wait_for_user("\n\nPress ENTER to continue to Part 3")

            # Part 3: Group management concept
            self.demonstrate_group_creation_concept()
            wait_for_user("\n\nPress ENTER to continue to Part 4")

            # Part 4: Individual rights
            self.demonstrate_individual_rights_assignment()
            wait_for_user("\n\nPress ENTER to continue to Part 5")

            # Part 5: Verification
            self.demonstrate_rights_verification()
            wait_for_user("\n\nPress ENTER to continue to Part 6")

            # Part 6: Collection rights
            self.demonstrate_collection_rights()

            # Final summary
            print_section_header("DEMO COMPLETE - KEY TAKEAWAYS")
            print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║              NAKALA Rights Management Best Practices                       ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ✓ Understand Rights Hierarchy                                             ║
║    • OWNER > ADMIN > EDITOR > READER > DEPOSITOR                           ║
║    • Creator automatically becomes OWNER                                   ║
║    • OWNER cannot be removed or changed                                    ║
║                                                                            ║
║  ✓ Use Groups for Team Collaboration                                       ║
║    • Create groups: POST /groups                                           ║
║    • Assign group rights: POST /datas/{id}/rights                          ║
║    • Manage team permissions efficiently                                   ║
║                                                                            ║
║  ✓ Assign Individual Rights for Flexibility                                ║
║    • Find user: GET /users/search?q=username                               ║
║    • Assign rights: POST /datas/{id}/rights                                ║
║    • Quick collaboration without groups                                    ║
║                                                                            ║
║  ✓ Always Verify Rights After Assignment                                   ║
║    • Check rights: GET /datas/{id}/rights                                  ║
║    • Verify expected roles are assigned                                    ║
║    • Catch configuration errors early                                      ║
║                                                                            ║
║  ✓ Remember: Collection ≠ Dataset Rights                                   ║
║    • Rights are independent per resource                                   ║
║    • Must assign separately                                                ║
║    • Design intentional access patterns                                    ║
║                                                                            ║
║  🎯 RECOMMENDATION: Start with EDITOR for collaborators!                   ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

Next Steps:
-----------
1. Design your project's access control strategy
2. Create groups for your research teams
3. Assign appropriate roles based on responsibilities
4. Regularly audit rights assignments
5. Review NAKALA_API_VISUAL_GUIDE.md for complete workflow

Happy collaborating on NAKALA! 🤝
            """)

        except Exception as e:
            print_error(f"\nDemo error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            wait_for_user("\n\nPress ENTER to cleanup test resources")
            self.cleanup()


def main():
    """Main entry point"""
    demo = RightsManagementDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()
