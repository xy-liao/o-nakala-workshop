"""
NAKALA Configuration
====================

Configuration constants for NAKALA API access.
"""

import os

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use defaults

# NAKALA API Configuration
API_URL = os.getenv('NAKALA_API_URL', 'https://apitest.nakala.fr')
API_KEY = os.getenv('NAKALA_API_KEY', 'aae99aba-476e-4ff2-2886-0aaf1bfa6fd2')  # Test API key

# NAKALA Property URIs (for metadata)
PROPERTY_URIS = {
    'title': 'http://nakala.fr/terms#title',
    'alternative': 'http://purl.org/dc/terms/alternative',
    'description': 'http://purl.org/dc/terms/description',
    'subject': 'http://purl.org/dc/terms/subject',
    'creator': 'http://nakala.fr/terms#creator',
    'contributor': 'http://purl.org/dc/terms/contributor',
    'created': 'http://nakala.fr/terms#created',
    'license': 'http://nakala.fr/terms#license',
    'type': 'http://nakala.fr/terms#type',
    'language': 'http://purl.org/dc/terms/language',
    'temporal': 'http://purl.org/dc/terms/temporal',
    'spatial': 'http://purl.org/dc/terms/spatial',
    'accessRights': 'http://purl.org/dc/terms/accessRights',
    'identifier': 'http://purl.org/dc/terms/identifier',
    'publisher': 'http://purl.org/dc/terms/publisher',
}

# Rate limiting
RATE_LIMIT_DELAY = 1.0  # seconds between requests

# Demo-specific constants (used by demonstration scripts)
DEMO_CREATOR = {
    "givenname": "Demo",
    "surname": "User",
    "fullName": "Demo User",
    "orcid": "0000-0002-1825-0097"  # Example ORCID
}

DEMO_LICENSE = "CC-BY-4.0"
DEMO_TYPE_URI = "http://purl.org/coar/resource_type/c_c513"  # Image

# Interactive mode for demonstrations
INTERACTIVE_MODE = os.getenv('NAKALA_INTERACTIVE_MODE', 'true').lower() == 'true'
