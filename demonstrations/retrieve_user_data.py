#!/usr/bin/env python3
"""
NAKALA User Data Retrieval Demonstration
========================================

Bonus script for retrieving and organizing user data:
1. User info retrieval
2. Datasets belonging to the user
3. Collections belonging to the user
4. Datasets organized in associated collections

Usage:
    python retrieve_user_data.py
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path to allow importing nakala package
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import from nakala package
from nakala import API_URL, API_KEY, RATE_LIMIT_DELAY
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

class RetrieveUserDataDemo:
    """
    Demonstration of retrieving and organizing user data from NAKALA
    """

    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY
        self.username = None
        self.datasets = []
        self.collections = []

    def step_1_get_user_info(self):
        """Step 1: Retrieve User Information"""
        print_step_header(1, "Retrieve User Information", "GET")

        print_info("Retrieving the authenticated user's profile...")

        response = make_api_request('GET', '/users/me')

        if response.status_code == 200:
            user_data = response.json()
            self.username = user_data.get('username')
            full_name = user_data.get('fullname') or user_data.get('fullName', 'Unknown')

            print_success(f"User found: {self.username} ({full_name})")
            print_info(f"   Email: {user_data.get('mail', 'N/A')}")
        else:
            print_error(f"Could not retrieve /users/me (Status: {response.status_code})")
            print_info("Check the API key in nakala/config.py (or NAKALA_API_KEY).")
            raise RuntimeError("Authentication failed")

    def step_2_retrieve_datasets(self):
        """Step 2: Retrieve Datasets belonging to the user"""
        print_step_header(2, f"Retrieve Datasets for {self.username}", "GET")
        
        print_info(f"Searching for datasets owned by {self.username} (user=me)...")

        page = 1
        size = 25  # NAKALA /search paginates with 'size', not 'limit'
        max_pages = 5  # Limit for demonstration purposes

        while page <= max_pages:
            # Use user=me to search for resources owned by the authenticated user
            # Filter by type=Data (http://nakala.fr/terms/Data)
            endpoint = f"/search?user=me&type=http://nakala.fr/terms/Data&page={page}&size={size}"
            response = make_api_request('GET', endpoint)

            if response.status_code == 200:
                data = response.json()
                results = data.get('datas', [])

                if not results:
                    if page == 1:
                        print_info("No datasets found.")
                    break
                
                for item in results:
                    # Extract useful info
                    ds_info = {
                        'id': item.get('identifier'),
                        'title': self._get_title(item),
                        'status': item.get('status'),
                        'collections': item.get('collections', [])
                    }
                    self.datasets.append(ds_info)
                    print_info(f"   Found Dataset: {ds_info['id']} - {ds_info['title'][:50]}...")

                if len(results) < size:
                    break
                page += 1
                time.sleep(RATE_LIMIT_DELAY)
            else:
                print_error(f"Failed to search datasets: {response.status_code}")
                break
        
        print_success(f"Total Datasets Found: {len(self.datasets)}")

    def step_3_retrieve_collections(self):
        """Step 3: Retrieve Collections belonging to the user"""
        print_step_header(3, f"Retrieve Collections for {self.username}", "GET")
        
        print_info(f"Searching for collections owned by {self.username} (user=me)...")

        page = 1
        size = 25  # NAKALA /search paginates with 'size', not 'limit'

        while True:
            # Use user=me and filter by type=Collection
            endpoint = f"/search?user=me&type=http://nakala.fr/terms/Collection&page={page}&size={size}"
            response = make_api_request('GET', endpoint)

            if response.status_code == 200:
                data = response.json()
                results = data.get('datas', [])

                if not results:
                    if page == 1:
                        print_info("No collections found.")
                    break
                
                for item in results:
                    col_info = {
                        'id': item.get('identifier'),
                        'title': self._get_title(item),
                        'status': item.get('status'),
                        'dataset_ids': []
                    }
                    self.collections.append(col_info)
                    print_info(f"   Found Collection: {col_info['id']} - {col_info['title'][:50]}...")

                if len(results) < size:
                    break
                page += 1
                time.sleep(RATE_LIMIT_DELAY)
            else:
                print_error(f"Failed to search collections: {response.status_code}")
                break
                
        print_success(f"Total Collections Found: {len(self.collections)}")

    def step_4_organize_data(self):
        """Step 4: Organize and Display Data (Datasets in Collections)"""
        print_step_header(4, "Organize Datasets in Collections", "PROCESS")
        
        # Link datasets to collections by fetching each collection's content
        # (/collections/{id}/datas), which is authoritative. The 'collections'
        # field on dataset search results is a faster but less reliable shortcut.
        print_info("Fetching content for each collection...")
        
        collection_map = {c['id']: c for c in self.collections}
        # Also keep a list of datasets that are NOT in any of our retrieved collections
        datasets_in_collections = set()
        
        for col in self.collections:
            col_id = col['id']
            print_info(f"   Fetching datasets for collection {col_id}...")
            
            # Endpoint to get datasets in a collection
            response = make_api_request('GET', f'/collections/{col_id}/datas')
            
            if response.status_code == 200:
                col_datas = response.json()
                # /collections/{id}/datas returns either a bare list of dataset
                # objects or a paginated wrapper with a 'data' key
                items = col_datas if isinstance(col_datas, list) else col_datas.get('data', [])
                
                for item in items:
                    ds_id = item.get('identifier')
                    if ds_id:
                        collection_map[col_id]['dataset_ids'].append(ds_id)
                        datasets_in_collections.add(ds_id)
            
            time.sleep(RATE_LIMIT_DELAY)

        # Now Display the Hierarchy
        print_section_header(f"USER DATA REPORT: {self.username}")
        
        print("\n📂 COLLECTIONS:")
        if not self.collections:
            print("   (No collections)")
        
        for col in self.collections:
            print(f"\n   📦 Collection: {col['title']} ({col['id']})")
            print(f"      Status: {col['status']}")
            ds_ids = col['dataset_ids']
            if ds_ids:
                print(f"      Datasets ({len(ds_ids)}):")
                for ds_id in ds_ids:
                    # Find title from our dataset list if possible
                    ds_title = next((d['title'] for d in self.datasets if d['id'] == ds_id), "Unknown Title")
                    print(f"        📄 {ds_title} ({ds_id})")
            else:
                print("      (Empty collection)")

        # List datasets not in any collection (Orphans)
        print("\n📄 UNORGANIZED DATASETS (Not in above collections):")
        orphans = [d for d in self.datasets if d['id'] not in datasets_in_collections]
        
        if orphans:
            for ds in orphans:
                print(f"   📄 {ds['title']} ({ds['id']})")
        else:
            print("   (None - all retrieved datasets are in collections)")

    def _get_title(self, item: Dict[str, Any]) -> str:
        """Helper to extract title from metadata"""
        metas = item.get('metas', [])
        for meta in metas:
            if meta.get('propertyUri') == 'http://nakala.fr/terms#title':
                return meta.get('value', 'Untitled')
        return 'Untitled'

    def run(self):
        """Run the full demonstration"""
        print_section_header("NAKALA USER DATA RETRIEVAL DEMO")
        wait_for_user("Press ENTER to start")
        
        try:
            self.step_1_get_user_info()
            wait_for_user()
            
            self.step_2_retrieve_datasets()
            wait_for_user()
            
            self.step_3_retrieve_collections()
            wait_for_user()
            
            self.step_4_organize_data()
            
            print_section_header("DEMONSTRATION COMPLETE")
            
        except Exception as e:
            print_error(f"An error occurred: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    demo = RetrieveUserDataDemo()
    demo.run()

if __name__ == '__main__':
    main()
