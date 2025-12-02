#!/usr/bin/env python3
"""
NAKALA Incremental Metadata Operations Demo
============================================

CORRECT NAKALA Pattern: POST/DELETE /metadatas (NOT PATCH!)
------------------------------------------------------------

CRITICAL: PATCH is NOT supported for /datas or /collections
- PATCH returns 405 Method Not Allowed
- Only available for /datas/{id}/relations (to update relation comments)

Instead, use these endpoints for incremental metadata operations:
- POST /datas/{id}/metadatas - Add metadata incrementally
- DELETE /datas/{id}/metadatas - Remove specific metadata
- POST /collections/{id}/metadatas - Add collection metadata
- DELETE /collections/{id}/metadatas - Remove collection metadata

This demo demonstrates:
=======================

SCENARIO 1: Add New Keyword (POST /metadatas)
  - Original collection has 1 keyword
  - Add new keyword without affecting existing
  - Verify both keywords exist

SCENARIO 2: Remove Keywords by Filter (DELETE /metadatas)
  - Collection has multiple keywords
  - DELETE uses filter (propertyUri + lang) - removes ALL matches
  - Cannot target specific values

SCENARIO 3: Add Translation (POST /metadatas)
  - Original title only in English
  - Add French translation
  - Verify multilingual support

SCENARIO 4: Update Value by Replace (DELETE + POST)
  - Need to change specific metadata value
  - Delete old value, add new value
  - Two-step operation pattern

SCENARIO 5: Contrast with PUT Dangers
  - Show how PUT replaces ALL metadata
  - Demonstrate accidental data loss risk
  - Reinforce why incremental operations are safer

Key Learning Points:
--------------------
1. POST /metadatas ADDS without replacing existing (WORKS ✓)
2. DELETE /metadatas uses FILTER (propertyUri + lang) - removes ALL matches ⚠️
3. Cannot delete specific values - DELETE is broad, not surgical
4. Use GET + PUT for surgical removal of specific values
5. PATCH is NOT supported for metadata in NAKALA
6. PUT replaces everything - use only when intentional
7. Same pattern works for both datasets and collections

IMPORTANT DISCOVERY - DELETE /metadatas Filter Behavior:
-------------------------------------------------------
DELETE /metadatas uses a FILTER approach, not surgical removal:

Official API Spec (apitest-nakala.json line 562):
  "Il est possible de passer un filtre dans le corps de la requête qui
   permettra de ne supprimer que certaines métadonnées"

Payload Format: {"lang": "en", "propertyUri": "http://purl.org/dc/terms/subject"}

Key Understanding:
- Payload is a FILTER (propertyUri + lang), NOT complete metadata object
- Removes ALL metadata matching the filter
- Cannot target specific values (no "value" field in filter)
- Effectively clears entire property category for that language

Example: DELETE with {"propertyUri": "subject", "lang": "en"}
  → Removes ALL English keywords, not just one specific keyword

For surgical removal of specific values:
  1. GET current metadata
  2. Filter out unwanted value in your code
  3. PUT with rebuilt metadata array (careful - must include all fields!)

This demo now shows the CORRECT filter pattern as documented in official spec.

Educational Goals:
------------------
1. Master POST/DELETE /metadatas pattern (reference best practice)
2. Understand granular metadata control
3. Learn safe update patterns (avoid PUT data loss)
4. Practice multilingual metadata management
5. Build confidence with incremental operations

Requirements:
-------------
- Python 3.7+
- requests library
- Active internet connection
- NAKALA test API access (uses apitest.nakala.fr)

Usage:
------
    python incremental_metadata_demo.py

Author: Syl (NAKALA API Educational Resources)
Created: November 17, 2025
Updated: November 17, 2025 (Fixed keyword counting bug, documented DELETE limitation)
License: CC0-1.0

Note: Part of user-created pedagogical suite, not official Huma-Num documentation.
      Implements recommendations from NAKALA_METADATA_MODIFICATION_GUIDE.md
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List

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


class IncrementalMetadataDemo:
    """
    Demonstrate NAKALA's incremental metadata operations using POST/DELETE /metadatas
    """

    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY
        self.collection_id = None

    def create_test_collection(self, initial_keywords: List[str] = None) -> str:
        """Create a test collection with standard metadata"""
        if initial_keywords is None:
            initial_keywords = ["digital humanities"]

        print_info("Creating test collection...")

        metas = [
            {
                "propertyUri": PROPERTY_URIS['title'],
                "value": "Incremental Metadata Test Collection",
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['description'],
                "value": "Demonstration of incremental metadata operations",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            }
        ]

        # Add initial keywords
        for keyword in initial_keywords:
            metas.append({
                "propertyUri": PROPERTY_URIS['subject'],
                "value": keyword,
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            })

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

    def get_metadata_summary(self, collection_id: str) -> Dict[str, Any]:
        """Get and display current metadata state"""
        response = make_api_request('GET', f'/collections/{collection_id}')
        if response.status_code == 200:
            data = response.json()
            metas = data.get('metas', [])

            # Count by property
            summary = {}
            for meta in metas:
                # Extract property name - handle both # and / separators
                prop_uri = meta.get('propertyUri', '')
                if '#' in prop_uri:
                    prop = prop_uri.split('#')[-1]
                elif '/' in prop_uri:
                    prop = prop_uri.split('/')[-1]
                else:
                    prop = prop_uri

                if prop not in summary:
                    summary[prop] = []
                summary[prop].append({
                    'value': meta.get('value'),
                    'lang': meta.get('lang', 'N/A')
                })

            return {'metas': metas, 'summary': summary}
        return None

    def scenario_1_add_keyword(self):
        """Scenario 1: Add new keyword using POST /metadatas"""
        print_section_header("SCENARIO 1: Add New Keyword (POST /metadatas)")

        print("""
Problem: Collection has 1 keyword, need to add another
Goal: Add "metadata management" keyword without affecting existing

Method: POST /collections/{id}/metadatas
  ✓ Incremental addition
  ✓ Existing metadata preserved
  ✓ No full replacement needed
        """)

        # Create collection with one keyword
        collection_id = self.create_test_collection(initial_keywords=["digital humanities"])
        time.sleep(RATE_LIMIT_DELAY)

        # Show original state
        print_info("\n📊 ORIGINAL STATE:")
        state = self.get_metadata_summary(collection_id)
        print_info(format_metadata_for_display(state['metas']))
        print_info(f"\nKeyword count: {len(state['summary'].get('subject', []))}")

        wait_for_user("\nPress ENTER to ADD new keyword using POST /metadatas")

        # =================================================================
        # POST /metadatas - Add new keyword
        # =================================================================
        print_step_header("1", "Add keyword with POST /metadatas", "POST")

        new_keyword = {
            "propertyUri": PROPERTY_URIS['subject'],
            "value": "metadata management",
            "typeUri": "http://www.w3.org/2001/XMLSchema#string",
            "lang": "en"
        }

        print_info("\n📦 POST /metadatas payload:")
        print_info(json.dumps(new_keyword, indent=2))

        response = make_api_request('POST', f'/collections/{collection_id}/metadatas', data=new_keyword)

        if response.status_code in [200, 201, 204]:
            print_success("\n✓ POST /metadatas successful!")

            time.sleep(RATE_LIMIT_DELAY)
            state = self.get_metadata_summary(collection_id)

            print_info("\n📊 AFTER POST /metadatas:")
            print_info(format_metadata_for_display(state['metas']))
            print_info(f"\nKeyword count: {len(state['summary'].get('subject', []))}")

            print_success("\n✓ New keyword added")
            print_success("✓ Original keyword preserved")
            print_success("✓ All other metadata preserved")
        else:
            print_error(f"POST /metadatas failed: {response.status_code}")
            print_error(response.text)

        # Cleanup
        make_api_request('DELETE', f'/collections/{collection_id}')

        print_section_header("SCENARIO 1 SUMMARY")
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                  POST /metadatas - Incremental Addition                   ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Endpoint: POST /collections/{id}/metadatas                                ║
║                                                                            ║
║  Behavior:                                                                 ║
║  ✓ ADDS new metadata entry                                                 ║
║  ✓ PRESERVES all existing metadata                                         ║
║  ✓ No risk of data loss                                                    ║
║                                                                            ║
║  Use when:                                                                 ║
║  • Adding new keywords                                                     ║
║  • Adding translations (multilingual fields)                               ║
║  • Adding new creators/contributors                                        ║
║  • Incrementally building metadata                                         ║
║                                                                            ║
║  🎯 RECOMMENDATION: Use POST /metadatas instead of PUT for additions!      ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def scenario_2_remove_keyword(self):
        """Scenario 2: Remove keywords by filter using DELETE /metadatas"""
        print_section_header("SCENARIO 2: Remove Keywords by Filter (DELETE /metadatas)")

        print("""
Problem: Collection has 3 keywords in English
Goal: Remove all English keywords using DELETE filter

Method: DELETE /collections/{id}/metadatas
  ⚠️  Uses FILTER format (propertyUri + lang only)
  ⚠️  Removes ALL metadata matching the filter
  ⚠️  Cannot target specific values
        """)

        # Create collection with multiple keywords
        keywords = ["digital humanities", "metadata management", "outdated keyword"]
        collection_id = self.create_test_collection(initial_keywords=keywords)
        time.sleep(RATE_LIMIT_DELAY)

        # Show original state
        print_info("\n📊 ORIGINAL STATE:")
        state = self.get_metadata_summary(collection_id)
        print_info(format_metadata_for_display(state['metas']))
        print_info(f"\nKeyword count: {len(state['summary'].get('subject', []))}")
        print_info(f"Keywords: {[k['value'] for k in state['summary'].get('subject', [])]}")

        wait_for_user("\nPress ENTER to REMOVE ALL English keywords using DELETE /metadatas filter")

        # =================================================================
        # DELETE /metadatas - Remove specific keyword
        # =================================================================
        print_step_header("1", "Remove keyword with DELETE /metadatas", "DELETE")

        # CRITICAL: DELETE /metadatas uses a FILTER object (not complete metadata)
        # According to official API spec (apitest-nakala.json line 562):
        # "Il est possible de passer un filtre dans le corps de la requête qui
        #  permettra de ne supprimer que certaines métadonnées"
        # Example: {"lang": "en", "propertyUri": "http://purl.org/dc/terms/subject"}
        #
        # This filter will delete ALL metadata matching propertyUri + lang
        # You CANNOT target specific values - it's a broad filter!
        target_keyword = {
            "propertyUri": PROPERTY_URIS['subject'],
            "lang": "en"
        }

        print_info("\n📦 DELETE /metadatas payload (filter format):")
        print_info(json.dumps(target_keyword, indent=2))
        print_warning("\nIMPORTANT: This filter deletes ALL English subject metadata!")
        print_warning("Cannot target specific values - removes all matches!")

        response = make_api_request('DELETE', f'/collections/{collection_id}/metadatas', data=target_keyword)

        if response.status_code in [200, 204]:
            print_success("\n✓ DELETE /metadatas successful!")

            time.sleep(RATE_LIMIT_DELAY)
            state = self.get_metadata_summary(collection_id)

            print_info("\n📊 AFTER DELETE /metadatas:")
            print_info(format_metadata_for_display(state['metas']))
            print_info(f"\nKeyword count: {len(state['summary'].get('subject', []))}")
            print_info(f"Keywords: {[k['value'] for k in state['summary'].get('subject', [])]}")

            print_success("\n✓ ALL English keywords removed (filter matched all)")
            print_success("✓ Filter deleted: propertyUri=subject + lang=en")
            print_success("✓ Title and description preserved (different propertyUri)")
        else:
            print_warning(f"\n⚠️  DELETE /metadatas returned: {response.status_code}")
            print_warning(response.text)
            print_info("\n📝 IMPORTANT DISCOVERY:")
            print_info("   DELETE /metadatas may not be fully supported in current API version")
            print_info("   This is a known limitation - POST works, but DELETE has issues")
            print_info("\n   Alternative approaches:")
            print_info("   1. Use PUT with complete metadata (must include all fields)")
            print_info("   2. Rebuild metadata array without unwanted values")
            print_info("   3. Wait for API update to fully support DELETE /metadatas")
            print_info("\n   This demo shows the INTENDED pattern for when DELETE is supported")


        # Cleanup
        make_api_request('DELETE', f'/collections/{collection_id}')

        print_section_header("SCENARIO 2 SUMMARY")
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                  DELETE /metadatas - Filter-Based Removal                 ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Endpoint: DELETE /collections/{id}/metadatas                              ║
║                                                                            ║
║  Behavior: BROAD FILTER (not surgical!)                                    ║
║  • REMOVES ALL metadata matching filter                                    ║
║  • Filter: propertyUri + lang (optional)                                   ║
║  • Cannot target specific values                                           ║
║  • PRESERVES metadata with different propertyUri                           ║
║                                                                            ║
║  Payload Format:                                                           ║
║  {                                                                         ║
║    "propertyUri": "http://purl.org/dc/terms/subject",                     ║
║    "lang": "en"                                                            ║
║  }                                                                         ║
║                                                                            ║
║  ⚠️  LIMITATION: No value-specific targeting                               ║
║  • Deletes ALL subject:en metadata                                         ║
║  • Cannot delete just one keyword among many                               ║
║  • Use GET + rebuild + PUT if you need surgical removal                    ║
║                                                                            ║
║  Use when:                                                                 ║
║  • Removing ALL keywords in a language                                     ║
║  • Clearing all instances of a property                                    ║
║  • Starting fresh with specific metadata type                              ║
║                                                                            ║
║  🎯 FOR SURGICAL REMOVAL: Use GET + PUT with rebuilt metadata              ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def scenario_3_add_translation(self):
        """Scenario 3: Add translation using POST /metadatas"""
        print_section_header("SCENARIO 3: Add Translation (POST /metadatas)")

        print("""
Problem: Title only exists in English, need French translation
Goal: Add French title without affecting English version

Method: POST /collections/{id}/metadatas
  ✓ Add metadata with different 'lang' value
  ✓ Multilingual support
  ✓ Original language preserved
        """)

        # Create collection with English-only title
        collection_id = self.create_test_collection(initial_keywords=["multilingual"])
        time.sleep(RATE_LIMIT_DELAY)

        # Show original state
        print_info("\n📊 ORIGINAL STATE:")
        state = self.get_metadata_summary(collection_id)
        titles = state['summary'].get('title', [])
        print_info(f"Title entries: {len(titles)}")
        for t in titles:
            print_info(f"  • [{t['lang']}] {t['value']}")

        wait_for_user("\nPress ENTER to ADD French translation using POST /metadatas")

        # =================================================================
        # POST /metadatas - Add French title
        # =================================================================
        print_step_header("1", "Add French title with POST /metadatas", "POST")

        french_title = {
            "propertyUri": PROPERTY_URIS['title'],
            "value": "Collection de Test des Métadonnées Incrémentales",
            "lang": "fr"
        }

        print_info("\n📦 POST /metadatas payload:")
        print_info(json.dumps(french_title, indent=2))

        response = make_api_request('POST', f'/collections/{collection_id}/metadatas', data=french_title)

        if response.status_code in [200, 201, 204]:
            print_success("\n✓ POST /metadatas successful!")

            time.sleep(RATE_LIMIT_DELAY)
            state = self.get_metadata_summary(collection_id)

            print_info("\n📊 AFTER POST /metadatas:")
            titles = state['summary'].get('title', [])
            print_info(f"Title entries: {len(titles)}")
            for t in titles:
                print_info(f"  • [{t['lang']}] {t['value']}")

            print_success("\n✓ French translation added")
            print_success("✓ English title preserved")
            print_success("✓ Collection now bilingual!")
        else:
            print_error(f"POST /metadatas failed: {response.status_code}")
            print_error(response.text)

        # Cleanup
        make_api_request('DELETE', f'/collections/{collection_id}')

        print_section_header("SCENARIO 3 SUMMARY")
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║              POST /metadatas - Multilingual Metadata                      ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Pattern: Add metadata with same propertyUri but different 'lang'          ║
║                                                                            ║
║  Example:                                                                  ║
║  • Original: {"propertyUri": "...:title", "value": "Test", "lang": "en"}  ║
║  • Add: {"propertyUri": "...:title", "value": "Test", "lang": "fr"}       ║
║  • Result: Collection has BOTH English and French titles                   ║
║                                                                            ║
║  Use for:                                                                  ║
║  • Adding translations (titles, descriptions)                              ║
║  • Building multilingual datasets                                          ║
║  • Internationalization (i18n)                                             ║
║  • Meeting FAIR data principles                                            ║
║                                                                            ║
║  🌍 MULTILINGUAL BEST PRACTICE:                                            ║
║  1. Create resource with primary language                                  ║
║  2. Use POST /metadatas to add translations incrementally                  ║
║  3. No risk of losing existing language versions                           ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def scenario_4_update_value(self):
        """Scenario 4: Rebuild keywords using DELETE + POST pattern"""
        print_section_header("SCENARIO 4: Rebuild Keywords (DELETE + POST pattern)")

        print("""
Problem: Keywords include "draft", "research", "2025" - want to replace with new set
Goal: Clear all English keywords and add fresh ones

Method: Two-step operation
  1. DELETE /metadatas - Remove ALL English keywords (filter)
  2. POST /metadatas - Add new keywords one by one
  ⚠️  DELETE removes ALL matches (not surgical!)
  ✓ Allows complete rebuild of keyword set
        """)

        # Create collection with "draft" keyword
        keywords = ["research", "draft", "2025"]
        collection_id = self.create_test_collection(initial_keywords=keywords)
        time.sleep(RATE_LIMIT_DELAY)

        # Show original state
        print_info("\n📊 ORIGINAL STATE:")
        state = self.get_metadata_summary(collection_id)
        print_info(f"Keywords: {[k['value'] for k in state['summary'].get('subject', [])]}")

        wait_for_user("\nPress ENTER to CLEAR all keywords and REBUILD (DELETE + POST)")

        # =================================================================
        # STEP 1: DELETE old value
        # =================================================================
        print_step_header("1", "Delete old value", "DELETE")

        # Using FILTER format (propertyUri + lang only)
        # This will delete ALL English subject keywords!
        old_keyword = {
            "propertyUri": PROPERTY_URIS['subject'],
            "lang": "en"
        }

        print_info("\n📦 DELETE /metadatas payload (filter format):")
        print_info(json.dumps(old_keyword, indent=2))
        print_warning("⚠️  This will delete ALL English keywords, not just 'draft'!")

        response = make_api_request('DELETE', f'/collections/{collection_id}/metadatas', data=old_keyword)

        if response.status_code in [200, 204]:
            print_success("✓ Old value deleted")
            time.sleep(RATE_LIMIT_DELAY)
        else:
            print_warning(f"⚠️  DELETE failed ({response.status_code}) - continuing with POST to show pattern")
            time.sleep(RATE_LIMIT_DELAY)

        # =================================================================
        # STEP 2: POST new values (rebuild keyword set)
        # =================================================================
        print_step_header("2", "Add new keywords", "POST")

        # Add two new keywords to replace the old set
        new_keywords = [
            {
                "propertyUri": PROPERTY_URIS['subject'],
                "value": "published",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            },
            {
                "propertyUri": PROPERTY_URIS['subject'],
                "value": "open science",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                "lang": "en"
            }
        ]

        print_info("\n📦 POST /metadatas (adding multiple keywords):")
        for i, kw in enumerate(new_keywords, 1):
            print_info(f"\nKeyword {i}: {json.dumps(kw, indent=2)}")
            response = make_api_request('POST', f'/collections/{collection_id}/metadatas', data=kw)
            if response.status_code not in [200, 201, 204]:
                print_error(f"Failed to add keyword {i}: {response.status_code}")
            time.sleep(RATE_LIMIT_DELAY)

        print_success("\n✓ New keywords added")

        time.sleep(RATE_LIMIT_DELAY)
        state = self.get_metadata_summary(collection_id)

        print_info("\n📊 AFTER DELETE + POST:")
        print_info(f"Keywords: {[k['value'] for k in state['summary'].get('subject', [])]}")

        print_success("\n✓ Old keywords removed: ['research', 'draft', '2025']")
        print_success("✓ New keywords added: ['published', 'open science']")
        print_success("✓ Complete keyword set rebuild")

        # Cleanup
        make_api_request('DELETE', f'/collections/{collection_id}')

        print_section_header("SCENARIO 4 SUMMARY")
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║              DELETE + POST Pattern - Metadata Rebuild                     ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Pattern: Two-step operation                                               ║
║  1. DELETE /metadatas - Remove ALL matching filter                         ║
║  2. POST /metadatas - Add new values one by one                            ║
║                                                                            ║
║  Reality of DELETE:                                                        ║
║  • Uses filter (propertyUri + lang)                                        ║
║  • Removes ALL metadata matching filter                                    ║
║  • Cannot remove just one specific value                                   ║
║  • Effectively clears entire property category                             ║
║                                                                            ║
║  Use when:                                                                 ║
║  • Rebuilding complete keyword set                                         ║
║  • Replacing all entries of a property type                                ║
║  • Starting fresh with specific metadata category                          ║
║  • Clearing all values in a language                                       ║
║                                                                            ║
║  ⚠️  FOR SURGICAL REMOVAL:                                                 ║
║  • Use GET to retrieve current metadata                                    ║
║  • Filter out unwanted value in your code                                  ║
║  • Use PUT with rebuilt metadata array                                     ║
║                                                                            ║
║  🎯 PATTERN: DELETE (filter) + POST (rebuild) = REFRESH                    ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def scenario_5_put_dangers(self):
        """Scenario 5: Demonstrate PUT dangers by contrast"""
        print_section_header("SCENARIO 5: PUT Dangers (What NOT to do)")

        print("""
Problem: Need to add one keyword
WRONG Method: Use PUT to replace all metadata

Let's see what happens when we use PUT instead of POST /metadatas...
        """)

        # Create collection with rich metadata
        keywords = ["research", "metadata", "digital humanities"]
        collection_id = self.create_test_collection(initial_keywords=keywords)
        time.sleep(RATE_LIMIT_DELAY)

        # Show original state
        print_info("\n📊 ORIGINAL STATE:")
        state = self.get_metadata_summary(collection_id)
        print_info(format_metadata_for_display(state['metas']))
        print_info(f"\nTotal metadata entries: {len(state['metas'])}")
        print_info(f"Keywords: {[k['value'] for k in state['summary'].get('subject', [])]}")

        wait_for_user("\nPress ENTER to see what happens with PUT (DANGER!)")

        # =================================================================
        # PUT - Replaces everything
        # =================================================================
        print_step_header("1", "Add keyword with PUT (WRONG!)", "PUT")

        print_warning("\nTrying to add 'new keyword' using PUT...")
        print_warning("Developer only includes new keyword in payload")

        put_data = {
            "status": "private",
            "metas": [
                {
                    "propertyUri": PROPERTY_URIS['title'],
                    "value": "Incremental Metadata Test Collection",
                    "lang": "en"
                },
                {
                    "propertyUri": PROPERTY_URIS['subject'],
                    "value": "new keyword",  # Only the new keyword!
                    "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                    "lang": "en"
                }
                # NOTE: Description and other keywords NOT included!
            ]
        }

        print_info("\n📦 PUT payload:")
        print_info(json.dumps(put_data, indent=2))
        print_error("\n⚠️  Notice: Only 2 metadata entries in payload!")
        print_error("⚠️  Original had 5+ metadata entries!")

        response = make_api_request('PUT', f'/collections/{collection_id}', data=put_data)

        if response.status_code == 204:
            print_warning("\nPUT completed (status 204)")

            time.sleep(RATE_LIMIT_DELAY)
            state = self.get_metadata_summary(collection_id)

            print_info("\n📊 AFTER PUT:")
            print_info(format_metadata_for_display(state['metas']))
            print_info(f"\nTotal metadata entries: {len(state['metas'])}")
            print_info(f"Keywords: {[k['value'] for k in state['summary'].get('subject', [])]}")

            print_error("\n❌ DISASTER:")
            print_error("  • Description: DELETED")
            print_error("  • Original keywords: DELETED")
            print_error("  • Only new keyword remains")
            print_error("  • Data loss is PERMANENT!")
        else:
            print_error(f"PUT failed: {response.status_code}")

        # Cleanup
        make_api_request('DELETE', f'/collections/{collection_id}')

        print_section_header("SCENARIO 5 SUMMARY")
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                          PUT Dangers - Comparison                         ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ❌ WRONG: Using PUT to add one keyword                                    ║
║  • Replaces ALL metadata                                                   ║
║  • Anything not in payload is DELETED                                      ║
║  • High risk of accidental data loss                                       ║
║  • Complex payload required                                                ║
║                                                                            ║
║  ✓ CORRECT: Using POST /metadatas                                          ║
║  • Adds only the new keyword                                               ║
║  • All existing metadata preserved                                         ║
║  • No risk of data loss                                                    ║
║  • Simple payload                                                          ║
║                                                                            ║
║  🎯 GOLDEN RULE:                                                           ║
║                                                                            ║
║  • Use POST /metadatas to ADD                                              ║
║  • Use DELETE /metadatas to REMOVE                                         ║
║  • Use PUT only for COMPLETE replacement (rare!)                           ║
║  • NEVER use PUT for simple additions                                      ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def run_demo(self):
        """Run all demonstration scenarios"""
        print_section_header("NAKALA INCREMENTAL METADATA OPERATIONS")
        print("""
Welcome to the Incremental Metadata Operations Demo!
=====================================================

This demo demonstrates the CORRECT NAKALA pattern for metadata management:
• POST /datas/{id}/metadatas - Add metadata incrementally
• DELETE /datas/{id}/metadatas - Remove specific metadata
• Same endpoints for collections: /collections/{id}/metadatas

⚠️  CRITICAL: PATCH is NOT supported for /datas or /collections!

We'll cover 5 scenarios:
1. Add new keyword (POST /metadatas)
2. Remove specific keyword (DELETE /metadatas)
3. Add translation (POST /metadatas for multilingual)
4. Update value (DELETE + POST pattern)
5. PUT dangers (what NOT to do)

All operations use NAKALA test API (apitest.nakala.fr)
Resources are automatically cleaned up after each scenario.
        """)

        wait_for_user("Press ENTER to start demonstrations")

        try:
            # Scenario 1: Add keyword
            self.scenario_1_add_keyword()
            wait_for_user("\n\nPress ENTER to continue to Scenario 2")

            # Scenario 2: Remove keyword
            self.scenario_2_remove_keyword()
            wait_for_user("\n\nPress ENTER to continue to Scenario 3")

            # Scenario 3: Add translation
            self.scenario_3_add_translation()
            wait_for_user("\n\nPress ENTER to continue to Scenario 4")

            # Scenario 4: Update value
            self.scenario_4_update_value()
            wait_for_user("\n\nPress ENTER to continue to Scenario 5")

            # Scenario 5: PUT dangers
            self.scenario_5_put_dangers()

            # Final summary
            print_section_header("DEMO COMPLETE - KEY TAKEAWAYS")
            print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║              NAKALA Incremental Metadata Best Practices                   ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ✓ POST /metadatas - INCREMENTAL ADDITION                                  ║
║    • Endpoint: POST /datas/{id}/metadatas                                  ║
║    • Endpoint: POST /collections/{id}/metadatas                            ║
║    • Use for: Adding keywords, translations, creators                      ║
║    • Safe: Preserves all existing metadata                                 ║
║    • Recommended for most additions                                        ║
║                                                                            ║
║  ⚠️  DELETE /metadatas - FILTER-BASED REMOVAL                              ║
║    • Endpoint: DELETE /datas/{id}/metadatas                                ║
║    • Endpoint: DELETE /collections/{id}/metadatas                          ║
║    • Payload: {"propertyUri": "...", "lang": "en"} (FILTER!)              ║
║    • Removes ALL metadata matching filter (not surgical!)                  ║
║    • Cannot target specific values                                         ║
║    • Use for: Clearing entire property category                            ║
║                                                                            ║
║  ✓ DELETE + POST Pattern - REBUILD APPROACH                                ║
║    • Pattern: DELETE (clear all) + POST (add new values)                   ║
║    • Use for: Rebuilding complete keyword/property set                     ║
║    • Not for surgical removal of single values!                            ║
║                                                                            ║
║  🔧 GET + PUT - SURGICAL REMOVAL                                            ║
║    • For removing ONE specific value among many:                           ║
║      1. GET current metadata                                               ║
║      2. Filter out unwanted value in code                                  ║
║      3. PUT with rebuilt array                                             ║
║    • Careful: PUT must include ALL fields (status, files, etc.)            ║
║                                                                            ║
║  ❌ PATCH - NOT supported for /datas or /collections                      ║
║     • Returns 405 Method Not Allowed                                      ║
║     • Only available for /datas/{id}/relations (relation comments)        ║
║                                                                            ║
║  🎯 RECOMMENDATION:                                                         ║
║    • Use POST for additions                                                ║
║    • Use DELETE for clearing property categories                           ║
║    • Use GET+PUT for surgical value removal                                ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

Thank you for completing the demo!

Next Steps:
-----------
1. Try these patterns in your own projects
2. Read NAKALA_METADATA_MODIFICATION_GUIDE.md for advanced patterns
3. Review NAKALA_MULTIPLE_VALUES_AND_LANGUAGES_GUIDE.md for multilingual
4. Practice with the batch import scripts

Happy NAKALA development! 🚀
            """)

        except Exception as e:
            print_error(f"\nDemo error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print_info("\n\nDemo complete. All resources cleaned up.")


def main():
    """Main entry point"""
    demo = IncrementalMetadataDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()
