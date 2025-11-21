"""
NAKALA API Python Package
==========================

A Python package for working with the NAKALA digital repository API.

Main modules:
- csv_converter: CSV to NAKALA JSON conversion
- api_client: API request functions
- config: Configuration and constants
- demo_helpers: Interactive demonstration utilities

Usage:
    # For batch scripts
    from nakala import CsvConverter, create_dataset, API_URL

    # For interactive demonstrations
    from nakala.demo_helpers import print_section_header, make_api_request

Author: Syl
License: CC0-1.0
"""

__version__ = "1.0.0"

# Import key classes and functions for easy access
from nakala.csv_converter import CsvConverter
from nakala.config import (
    API_URL,
    API_KEY,
    PROPERTY_URIS,
    RATE_LIMIT_DELAY,
    DEMO_CREATOR,
    DEMO_LICENSE,
    DEMO_TYPE_URI,
    INTERACTIVE_MODE
)
from nakala.api_client import (
    upload_file,
    create_dataset,
    create_collection,
    get_dataset,
    get_collection,
    modify_dataset,
    modify_collection,
    delete_dataset,
    delete_collection
)

# Demo helpers are available but not imported by default (use: from nakala.demo_helpers import ...)
# This keeps the main namespace clean for batch scripts
import nakala.demo_helpers

# Backward compatibility alias (deprecated, will be removed in v2.0)
NAKALACSVConverter = CsvConverter

__all__ = [
    # Version
    '__version__',

    # CSV Converter
    'CsvConverter',
    'NAKALACSVConverter',  # Deprecated alias for backward compatibility

    # Configuration
    'API_URL',
    'API_KEY',
    'PROPERTY_URIS',
    'RATE_LIMIT_DELAY',

    # Demo Configuration
    'DEMO_CREATOR',
    'DEMO_LICENSE',
    'DEMO_TYPE_URI',
    'INTERACTIVE_MODE',

    # API Client Functions
    'upload_file',
    'create_dataset',
    'create_collection',
    'get_dataset',
    'get_collection',
    'modify_dataset',
    'modify_collection',
    'delete_dataset',
    'delete_collection',
]
