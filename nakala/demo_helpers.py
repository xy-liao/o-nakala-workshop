"""
NAKALA API Demo Helper Functions
=================================

Interactive demonstration utilities for NAKALA API demonstrations.
Provides formatted output, API request helpers, and user interaction.
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from nakala.config import API_URL, API_KEY, RATE_LIMIT_DELAY


# Interactive mode (can be overridden by setting environment variable)
import os
INTERACTIVE_MODE = os.getenv('NAKALA_INTERACTIVE_MODE', 'true').lower() == 'true'


def make_api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    api_key: str = API_KEY,
    api_url: str = API_URL
) -> requests.Response:
    """
    Make an API request to NAKALA

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint (e.g., '/datas' or '/datas/{id}')
        data: JSON payload for POST/PUT/PATCH
        api_key: NAKALA API key
        api_url: NAKALA API base URL

    Returns:
        Response object
    """
    url = f"{api_url}{endpoint}"
    headers = {'X-API-KEY': api_key}

    if data:
        headers['Content-Type'] = 'application/json'

    print_info(f"📡 {method} {endpoint}")

    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, data=json.dumps(data) if data else None)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, data=json.dumps(data) if data else None)
    elif method == 'PATCH':
        response = requests.patch(url, headers=headers, data=json.dumps(data) if data else None)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers, data=json.dumps(data) if data else None)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    # Log response
    status_emoji = "✓" if response.status_code in [200, 201, 204] else "✗"
    print_info(f"   {status_emoji} Response: {response.status_code}")

    return response


def print_section_header(title: str):
    """Print a major section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_step_header(step_num: int, title: str, method: str = ""):
    """Print a step header with method badge"""
    print("\n" + "-" * 80)
    method_badge = f" [{method}]" if method else ""
    print(f"STEP {step_num}: {title}{method_badge}")
    print("-" * 80)


def print_success(message: str):
    """Print success message"""
    print(f"✓ {message}")


def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️  {message}")


def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")


def print_info(message: str):
    """Print info message"""
    print(f"   {message}")


def print_json_comparison(before: Dict[str, Any], after: Dict[str, Any], title: str = "COMPARISON"):
    """
    Print before/after JSON comparison

    Args:
        before: State before modification
        after: State after modification
        title: Comparison title
    """
    print(f"\n📊 {title}")
    print("\n🔹 BEFORE:")
    print(json.dumps(before, indent=2, ensure_ascii=False))
    print("\n🔹 AFTER:")
    print(json.dumps(after, indent=2, ensure_ascii=False))

    # Extract differences
    differences = extract_differences(before, after)
    if differences:
        print("\n🔍 CHANGES DETECTED:")
        for diff in differences:
            print(f"   - {diff}")
    else:
        print("\n🔍 NO CHANGES DETECTED")


def extract_differences(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    """
    Extract differences between two dictionaries

    Args:
        before: Original state
        after: New state

    Returns:
        List of difference descriptions
    """
    differences = []

    # Compare metas arrays
    if 'metas' in before and 'metas' in after:
        before_metas = {
            (m.get('propertyUri'), m.get('lang', 'no-lang'), m.get('value', '')): m
            for m in before['metas']
        }
        after_metas = {
            (m.get('propertyUri'), m.get('lang', 'no-lang'), m.get('value', '')): m
            for m in after['metas']
        }

        # Find added metadata
        added = set(after_metas.keys()) - set(before_metas.keys())
        for key in added:
            uri, lang, value = key
            prop_name = uri.split('#')[-1].split('/')[-1]
            differences.append(f"Added {prop_name}: '{value[:50]}...'")

        # Find removed metadata
        removed = set(before_metas.keys()) - set(after_metas.keys())
        for key in removed:
            uri, lang, value = key
            prop_name = uri.split('#')[-1].split('/')[-1]
            differences.append(f"Removed {prop_name}: '{value[:50]}...'")

    # Compare status
    if before.get('status') != after.get('status'):
        differences.append(f"Status changed: {before.get('status')} → {after.get('status')}")

    # Compare datas (for collections)
    if 'datas' in before and 'datas' in after:
        before_datas = set(before.get('datas', []))
        after_datas = set(after.get('datas', []))

        added_datas = after_datas - before_datas
        removed_datas = before_datas - after_datas

        if added_datas:
            differences.append(f"Added {len(added_datas)} dataset(s)")
        if removed_datas:
            differences.append(f"Removed {len(removed_datas)} dataset(s)")

    return differences


def wait_for_user(message: str = "Press ENTER to continue to next step"):
    """Wait for user input if interactive mode is enabled"""
    if INTERACTIVE_MODE:
        input(f"\n⏸️  {message}... ")
    else:
        time.sleep(RATE_LIMIT_DELAY)


def print_method_comparison_table():
    """Print HTTP method comparison table for NAKALA datasets/collections"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   HTTP METHOD COMPARISON (NAKALA)                          ║
╠═══════════╦═══════════════╦═══════════════════╦═════════════════════════╣
║ Method    ║ Support       ║ Use Case          ║ What Changes            ║
╠═══════════╬═══════════════╬═══════════════════╬═════════════════════════╣
║ POST      ║ Yes           ║ Create new        ║ N/A (creates)           ║
║ GET       ║ Yes           ║ Read/retrieve     ║ Nothing (read-only)     ║
║ PATCH     ║ NO (405)      ║ Not supported     ║ Use /metadatas instead  ║
║ PUT       ║ Yes           ║ Complete replace  ║ Everything (DANGEROUS)  ║
║ DELETE    ║ Yes           ║ Remove entirely   ║ Everything (permanent)  ║
╚═══════════╩═══════════════╩═══════════════════╩═════════════════════════╝

🎯 NAKALA-SPECIFIC RECOMMENDATIONS:
   - Use POST to create datasets/collections
   - Use GET to verify state
   - Use POST/DELETE /metadatas for incremental updates (safest!)
   - Avoid PUT unless replacing everything (dangerous!)
   - Use DELETE with caution (permanent for pending, blocked for published)

⚠️  PATCH is NOT supported for /datas or /collections endpoints
""")


def print_status_lifecycle():
    """Print dataset status lifecycle diagram"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     DATASET STATUS LIFECYCLE                               ║
╚═══════════════════════════════════════════════════════════════════════════╝

  PENDING Status:
  ┌─────────────────────────────────────────────────────────────┐
  │ ✓ Can be modified with PUT or POST/DELETE /metadatas        │
  │ ✓ CAN be deleted with DELETE /datas/{id}                    │
  │ ✓ Can change to "published"                                 │
  │ ✓ Files restricted to authorized users                      │
  └─────────────────────────────────────────────────────────────┘
                              ↓
                  (status change to published)
                              ↓
  PUBLISHED Status:
  ┌─────────────────────────────────────────────────────────────┐
  │ ✓ Can be modified with PUT or POST/DELETE /metadatas        │
  │ ✗ CANNOT be deleted - permanent                             │
  │ ✗ CANNOT change back to pending                             │
  │ ✓ Gets DOI identifier                                       │
  │ ✓ Files public if embargo date ≤ today                      │
  └─────────────────────────────────────────────────────────────┘

⚠️  WARNING: Once published, deletion is IMPOSSIBLE!
""")


def format_metadata_for_display(metas: List[Dict[str, Any]]) -> str:
    """
    Format metadata array for readable display

    Args:
        metas: Metadata array from NAKALA response

    Returns:
        Formatted string
    """
    lines = []
    for meta in metas:
        uri = meta.get('propertyUri', '')
        prop_name = uri.split('#')[-1].split('/')[-1]
        value = meta.get('value', '')
        lang = meta.get('lang', '')

        # Handle creator format
        if isinstance(value, dict) and 'fullName' in value:
            value_str = value['fullName']
            if 'orcid' in value:
                value_str += f" (ORCID: {value['orcid']})"
        else:
            value_str = str(value)

        lang_str = f" [{lang}]" if lang else ""
        lines.append(f"   • {prop_name}{lang_str}: {value_str[:100]}")

    return "\n".join(lines)
