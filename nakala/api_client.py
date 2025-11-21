"""
NAKALA API Client
=================

Functions for interacting with the NAKALA API.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from nakala.config import API_URL

logger = logging.getLogger(__name__)


# ==============================================================================
# FILE OPERATIONS
# ==============================================================================

def upload_file(file_path: Path, api_key: str, api_url: str = API_URL) -> Optional[Dict[str, str]]:
    """
    Upload a file to NAKALA and return file metadata with sha1

    Args:
        file_path: Path to file
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Dict with 'name', 'sha1', 'embargoed' or None if failed
    """
    try:
        logger.info(f"Uploading file: {file_path.name}")

        with open(file_path, 'rb') as f:
            files = [('file', (file_path.name, f, 'application/octet-stream'))]
            headers = {'X-API-KEY': api_key}

            response = requests.post(
                f'{api_url}/datas/uploads',
                headers=headers,
                files=files
            )

            if response.status_code == 201:
                file_info = response.json()
                import time
                file_info['embargoed'] = time.strftime("%Y-%m-%d")  # Current date
                logger.info(f"✓ File uploaded: {file_path.name} (sha1: {file_info['sha1'][:8]}...)")
                return file_info
            else:
                logger.error(f"✗ File upload failed: {file_path.name} - {response.status_code}: {response.text}")
                return None

    except Exception as e:
        logger.error(f"✗ Error uploading file {file_path.name}: {str(e)}")
        return None


# ==============================================================================
# DATASET OPERATIONS
# ==============================================================================

def create_dataset(dataset: Dict[str, Any], api_key: str, api_url: str = API_URL) -> requests.Response:
    """
    Create a dataset on NAKALA

    Args:
        dataset: Dataset JSON structure
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Response object
    """
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': api_key
    }

    response = requests.post(
        f'{api_url}/datas',
        headers=headers,
        data=json.dumps(dataset)
    )

    return response


def get_dataset(dataset_id: str, api_key: str, api_url: str = API_URL) -> Optional[Dict[str, Any]]:
    """
    Get existing dataset from NAKALA

    Args:
        dataset_id: NAKALA dataset identifier
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Dataset JSON or None if not found
    """
    headers = {'X-API-KEY': api_key}

    try:
        response = requests.get(
            f'{api_url}/datas/{dataset_id}',
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Dataset not found: {dataset_id} - {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting dataset {dataset_id}: {str(e)}")
        return None


def modify_dataset(dataset_id: str, dataset: Dict[str, Any], api_key: str, api_url: str = API_URL) -> requests.Response:
    """
    Modify dataset on NAKALA (PUT - replaces all metadata)

    Args:
        dataset_id: NAKALA dataset identifier
        dataset: Dataset JSON structure (metas only)
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Response object
    """
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': api_key
    }

    response = requests.put(
        f'{api_url}/datas/{dataset_id}',
        headers=headers,
        data=json.dumps(dataset)
    )

    return response


def delete_dataset(dataset_id: str, api_key: str, api_url: str = API_URL) -> requests.Response:
    """
    Delete dataset from NAKALA

    Args:
        dataset_id: NAKALA dataset identifier
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Response object
    """
    headers = {'X-API-KEY': api_key}

    response = requests.delete(
        f'{api_url}/datas/{dataset_id}',
        headers=headers
    )

    return response


# ==============================================================================
# COLLECTION OPERATIONS
# ==============================================================================

def create_collection(collection: Dict[str, Any], api_key: str, api_url: str = API_URL) -> requests.Response:
    """
    Create a collection on NAKALA

    Args:
        collection: Collection JSON structure
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Response object
    """
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': api_key
    }

    response = requests.post(
        f'{api_url}/collections',
        headers=headers,
        data=json.dumps(collection)
    )

    return response


def get_collection(collection_id: str, api_key: str, api_url: str = API_URL) -> Optional[Dict[str, Any]]:
    """
    Get existing collection from NAKALA

    Args:
        collection_id: NAKALA collection identifier
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Collection JSON or None if not found
    """
    headers = {'X-API-KEY': api_key}

    try:
        response = requests.get(
            f'{api_url}/collections/{collection_id}',
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Collection not found: {collection_id} - {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting collection {collection_id}: {str(e)}")
        return None


def modify_collection(collection_id: str, collection: Dict[str, Any], api_key: str, api_url: str = API_URL) -> requests.Response:
    """
    Modify collection on NAKALA (PUT - replaces all metadata)

    Args:
        collection_id: NAKALA collection identifier
        collection: Collection JSON structure (metas only)
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Response object
    """
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': api_key
    }

    response = requests.put(
        f'{api_url}/collections/{collection_id}',
        headers=headers,
        data=json.dumps(collection)
    )

    return response


def delete_collection(collection_id: str, api_key: str, api_url: str = API_URL) -> requests.Response:
    """
    Delete collection from NAKALA

    Args:
        collection_id: NAKALA collection identifier
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Response object
    """
    headers = {'X-API-KEY': api_key}

    response = requests.delete(
        f'{api_url}/collections/{collection_id}',
        headers=headers
    )

    return response


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_dataset_info(dataset_id: str, api_key: str, api_url: str = API_URL) -> Optional[Dict[str, Any]]:
    """
    Get dataset info (wrapper around get_dataset for backward compatibility)

    Args:
        dataset_id: NAKALA dataset identifier
        api_key: NAKALA API key
        api_url: NAKALA API URL (default from config)

    Returns:
        Dataset info or None
    """
    return get_dataset(dataset_id, api_key, api_url)
