#!/usr/bin/env python3
"""
NAKALA Test Account Cleanup Script
==================================

WARNING: THIS SCRIPT DELETES DATA!
----------------------------------
This script cleans up a NAKALA Test API account by:
1. Deleting ALL collections owned by the user
2. Deleting ALL PENDING datasets owned by the user

It is designed to reset the test environment after workshop sessions.

Usage:
    python cleanup_nakala_test_account.py [--force] [--dry-run]

Options:
    --dry-run   Show what would be deleted without actually deleting (default)
    --force     Execute deletion without confirmation prompt (requires --no-dry-run)
"""

import sys
import time
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to allow importing nakala package
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from nakala import API_URL, API_KEY, RATE_LIMIT_DELAY
from nakala.demo_helpers import (
    make_api_request,
    print_section_header,
    print_success,
    print_warning,
    print_error,
    print_info
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class NakalaCleanup:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.api_url = API_URL
        self.api_key = API_KEY
        self.collections = []
        self.datasets = []

    def fetch_user_resources(self):
        """Fetch all resources owned by the current user"""
        print_section_header("FETCHING RESOURCES")
        print_info(f"Fetching resources for user (API Key: ...{self.api_key[-6:]})")
        
        page = 1
        limit = 100
        total_fetched = 0
        
        while True:
            print_info(f"  Fetching page {page}...")
            # make_api_request doesn't support params, so we construct the URL manually
            endpoint = f"/search?user=me&page={page}&size={limit}"
            response = make_api_request('GET', endpoint)
            
            if response.status_code != 200:
                print_error(f"Failed to fetch resources: {response.status_code}")
                sys.exit(1)
                
            data = response.json()
            items = data.get('datas', [])
            
            if not items:
                break
                
            for item in items:
                uri = item.get('uri', '')
                identifier = item.get('identifier')
                status = item.get('status')
                
                if '/collection/' in uri:
                    self.collections.append({
                        'id': identifier,
                        'status': status,
                        'title': self._get_title(item)
                    })
                else:
                    # If it's not a collection, it's a dataset
                    self.datasets.append({
                        'id': identifier,
                        'status': status,
                        'title': self._get_title(item)
                    })
            
            total_fetched += len(items)
            if total_fetched >= data.get('totalResults', 0):
                break
                
            page += 1
            time.sleep(RATE_LIMIT_DELAY)
            
        print_success(f"Found {len(self.collections)} collections and {len(self.datasets)} datasets")

    def _get_title(self, item: Dict[str, Any]) -> str:
        """Extract title from metadata list"""
        for meta in item.get('metas', []):
            if meta.get('propertyUri') == 'http://nakala.fr/terms#title':
                return meta.get('value', 'Untitled')
        return 'Untitled'

    def delete_collections(self):
        """Delete all collections"""
        print_section_header(f"DELETING COLLECTIONS ({len(self.collections)})")
        
        if not self.collections:
            print_info("No collections to delete.")
            return

        for col in self.collections:
            col_id = col['id']
            title = col['title']
            
            if self.dry_run:
                print_info(f"[DRY RUN] Would DELETE collection: {col_id} - '{title}'")
            else:
                print_info(f"Deleting collection: {col_id} - '{title}'...")
                response = make_api_request('DELETE', f'/collections/{col_id}')
                
                if response.status_code == 204:
                    print_success(f"  ✓ Deleted")
                elif response.status_code == 404:
                    print_warning(f"  ? Already deleted")
                else:
                    print_error(f"  ✗ Failed: {response.status_code}")
                
                time.sleep(RATE_LIMIT_DELAY)

    def delete_datasets(self):
        """Delete pending datasets"""
        pending_datasets = [d for d in self.datasets if d['status'] == 'pending']
        published_datasets = [d for d in self.datasets if d['status'] == 'published']
        
        print_section_header(f"DELETING DATASETS (Pending: {len(pending_datasets)}, Published: {len(published_datasets)})")
        
        if published_datasets:
            print_warning(f"Skipping {len(published_datasets)} published datasets (cannot be deleted via API)")
            
        if not pending_datasets:
            print_info("No pending datasets to delete.")
            return

        for ds in pending_datasets:
            ds_id = ds['id']
            title = ds['title']
            
            if self.dry_run:
                print_info(f"[DRY RUN] Would DELETE dataset: {ds_id} - '{title}'")
            else:
                print_info(f"Deleting dataset: {ds_id} - '{title}'...")
                response = make_api_request('DELETE', f'/datas/{ds_id}')
                
                if response.status_code == 204:
                    print_success(f"  ✓ Deleted")
                elif response.status_code == 404:
                    print_warning(f"  ? Already deleted")
                else:
                    print_error(f"  ✗ Failed: {response.status_code}")
                
                time.sleep(RATE_LIMIT_DELAY)

    def run(self):
        self.fetch_user_resources()
        
        print("\n" + "="*60)
        if self.dry_run:
            print_warning("DRY RUN MODE: No changes will be made.")
            print_info("Use --no-dry-run to actually delete resources.")
        else:
            print_warning("⚠️  LIVE MODE: RESOURCES WILL BE PERMANENTLY DELETED ⚠️")
        print("="*60 + "\n")
        
        self.delete_collections()
        self.delete_datasets()
        
        print_section_header("CLEANUP COMPLETE")

def main():
    parser = argparse.ArgumentParser(description='Cleanup NAKALA Test Account')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Simulate deletion (default)')
    parser.add_argument('--no-dry-run', action='store_false', dest='dry_run', help='Actually delete resources')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()

    # This script mass-deletes; it must never point anywhere but the test server.
    # config.py reads NAKALA_API_URL/NAKALA_API_KEY from the environment (or a
    # .env in the cwd), so refuse to run if that resolves to anything else.
    if 'apitest.nakala.fr' not in API_URL:
        print_error(f"Refusing to run against {API_URL}: this script is apitest-only.")
        print_info("Unset NAKALA_API_URL (and check for a .env in the current directory).")
        sys.exit(1)

    # Safety check
    if not args.dry_run and not args.force:
        print_warning("⚠️  WARNING: You are about to DELETE resources from NAKALA Test API.")
        print_warning("   - ALL Collections")
        print_warning("   - ALL Pending Datasets")
        response = input("\nAre you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print_info("Operation cancelled.")
            sys.exit(0)

    cleanup = NakalaCleanup(dry_run=args.dry_run)
    cleanup.run()

if __name__ == '__main__':
    main()
