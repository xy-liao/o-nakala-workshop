"""
CSV to NAKALA JSON Converter
=============================

Converts CSV rows to NAKALA API-compliant JSON structures.

Based on NAKALA_CSV_TO_JSON_CONVERTER_SPECIFICATION.md
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class CsvConverter:
    """
    Convert CSV rows to NAKALA API-compliant JSON structures

    This converter handles the transformation from user-friendly CSV format
    to the JSON structure required by the NAKALA API.

    Based on NAKALA_CSV_TO_JSON_CONVERTER_SPECIFICATION.md
    """

    def __init__(self):
        self.property_uris = {
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

    def parse_multilingual_field(self, value: str) -> List[Dict[str, str]]:
        """
        Parse: en: Title | zh: 標題 | fr: Titre
        Returns: [{"lang": "en", "value": "Title"}, {"lang": "zh", "value": "標題"}, ...]
        """
        if not value or value.strip() == "":
            return []

        # Check if multilingual format present
        if '|' not in value and ':' not in value:
            # Simple value, no language
            return [{"value": value.strip(), "lang": None}]

        result = []
        lang_parts = value.split('|')

        for part in lang_parts:
            part = part.strip()
            if ':' in part:
                # Split only on first colon
                lang, text = part.split(':', 1)
                result.append({
                    "lang": lang.strip(),
                    "value": text.strip()
                })
            else:
                # No language specified
                result.append({
                    "lang": None,
                    "value": part
                })

        return result

    def parse_multiple_values(self, value: str) -> List[str]:
        """
        Parse: key1 ; key2 ; key3
        Returns: ["key1", "key2", "key3"]
        """
        if ';' in value:
            return [v.strip() for v in value.split(';') if v.strip()]
        return [value.strip()] if value.strip() else []

    def normalize_orcid(self, orcid_str: str) -> Optional[str]:
        """
        Normalize ORCID identifier
        Accepts: 0000-0001-2345-6789, ORCID:0000-0001-2345-6789, https://orcid.org/0000-0001-2345-6789
        Returns: 0000-0001-2345-6789 or None if invalid
        """
        if not orcid_str:
            return None

        orcid = orcid_str.strip()

        # Strip common prefixes
        if orcid.startswith('https://orcid.org/'):
            orcid = orcid.replace('https://orcid.org/', '')
        elif orcid.startswith('http://orcid.org/'):
            orcid = orcid.replace('http://orcid.org/', '')
        elif orcid.upper().startswith('ORCID:'):
            orcid = orcid[6:].strip()

        # Validate format: XXXX-XXXX-XXXX-XXXX (last char can be X)
        if re.match(r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$', orcid):
            return orcid

        return None

    def parse_creator(self, value: str) -> List[Dict[str, Any]]:
        """
        Parse creator field with NAKALA "Surname, Given" format and optional ORCID

        Examples:
        - "Dupont, John (0000-0001-2345-6789)"
        - "Dupont, John (0000-0001-2345-6789);Lowey, Marc (0000-0002-3456-7890)"
        - "en:Dupont, John (0000-0001-2345-6789)|zh:杜工, 尚 (0000-0001-2345-6789)"

        Returns: List of creator metadata objects
        """
        if not value or value.strip() == "":
            return []

        creators = []

        # Regex to extract name and optional ORCID
        orcid_pattern = re.compile(r'^(.+?)\s*\(([0-9X-]{19})\)$')

        # Parse multilingual structure
        lang_parts = self.parse_multilingual_field(value)

        for lang_part in lang_parts:
            names_str = lang_part['value']

            # Split multiple creators by semicolon
            names = self.parse_multiple_values(names_str)

            for name in names:
                name = name.strip()
                orcid = None

                # Check for ORCID in parentheses
                match = orcid_pattern.match(name)
                if match:
                    name = match.group(1).strip()
                    orcid = self.normalize_orcid(match.group(2))

                # Parse "Surname, Given" format (NAKALA's "Dupont,Jean" format)
                if ',' in name:
                    parts = name.split(',', 1)
                    surname = parts[0].strip()
                    givenname = parts[1].strip() if len(parts) > 1 else ""
                else:
                    # Fallback: treat entire name as surname
                    surname = name
                    givenname = ""

                full_name = f"{givenname} {surname}".strip() if givenname else surname

                creator_value = {
                    "givenname": givenname,
                    "surname": surname,
                    "fullName": full_name
                }

                # Only add orcid if it's valid
                if orcid:
                    creator_value["orcid"] = orcid

                creators.append({
                    "propertyUri": self.property_uris['creator'],
                    "value": creator_value
                })

        return creators

    def parse_files(self, files_str: str, base_path: Path) -> List[Path]:
        """
        Parse: /path/file1.jpg | /path/file2.jpg | /path/folder/
        Returns: List of absolute file paths (expanding folders)
        """
        if not files_str or files_str.strip() == "":
            return []

        paths = [p.strip() for p in files_str.split('|') if p.strip()]
        files = []

        for path_str in paths:
            # Handle both absolute and relative paths
            if path_str.startswith('/'):
                path = Path(path_str)
            else:
                path = base_path / path_str

            if path.is_file():
                files.append(path.absolute())
            elif path.is_dir():
                # Expand folder to all files (recursive)
                for file_path in path.rglob('*'):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        files.append(file_path.absolute())
            else:
                logger.warning(f"Path not found: {path}")

        return files

    def csv_row_to_nakala_metas(self, row: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Convert CSV row to NAKALA metas array

        Args:
            row: Dictionary with CSV column names as keys

        Returns:
            List of NAKALA metadata objects
        """
        metas = []

        # Title (multilingual) - REQUIRED
        if row.get('title'):
            lang_parts = self.parse_multilingual_field(row['title'])
            for part in lang_parts:
                meta = {
                    "propertyUri": self.property_uris['title'],
                    "value": part['value']
                }
                if part['lang']:
                    meta['lang'] = part['lang']
                metas.append(meta)

        # Alternative title (multilingual)
        if row.get('alternative'):
            lang_parts = self.parse_multilingual_field(row['alternative'])
            for part in lang_parts:
                meta = {
                    "propertyUri": self.property_uris['alternative'],
                    "value": part['value'],
                    "typeUri": "http://www.w3.org/2001/XMLSchema#string"
                }
                if part['lang']:
                    meta['lang'] = part['lang']
                metas.append(meta)

        # Description (multilingual)
        if row.get('description'):
            lang_parts = self.parse_multilingual_field(row['description'])
            for part in lang_parts:
                meta = {
                    "propertyUri": self.property_uris['description'],
                    "value": part['value'],
                    "typeUri": "http://www.w3.org/2001/XMLSchema#string"
                }
                if part['lang']:
                    meta['lang'] = part['lang']
                metas.append(meta)

        # Subject/Keywords (multiple values + multilingual) - Use field name 'keywords'
        keywords_field = row.get('keywords') or row.get('subject')
        if keywords_field:
            lang_parts = self.parse_multilingual_field(keywords_field)
            for part in lang_parts:
                keywords = self.parse_multiple_values(part['value'])
                for keyword in keywords:
                    meta = {
                        "propertyUri": self.property_uris['subject'],
                        "value": keyword,
                        "typeUri": "http://www.w3.org/2001/XMLSchema#string"
                    }
                    if part['lang']:
                        meta['lang'] = part['lang']
                    metas.append(meta)

        # Creators (multiple + multilingual) - REQUIRED for published
        if row.get('creator'):
            creators = self.parse_creator(row['creator'])
            metas.extend(creators)

        # Contributors (multiple + multilingual)
        if row.get('contributor'):
            contributors = self.parse_creator(row['contributor'])  # Same format as creator
            # Change propertyUri to contributor
            for contrib in contributors:
                contrib['propertyUri'] = self.property_uris['contributor']
            metas.extend(contributors)

        # Created date (single value) - REQUIRED for published
        # Use field name 'date' or 'created'
        date_field = row.get('date') or row.get('created')
        if date_field:
            metas.append({
                "propertyUri": self.property_uris['created'],
                "value": date_field.strip(),
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            })

        # License (single value) - REQUIRED for published
        if row.get('license'):
            metas.append({
                "propertyUri": self.property_uris['license'],
                "value": row['license'].strip(),
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            })

        # Type (single value, URI) - REQUIRED
        if row.get('type'):
            metas.append({
                "propertyUri": self.property_uris['type'],
                "value": row['type'].strip(),
                "typeUri": "http://purl.org/dc/terms/URI"
            })

        # Language (single value)
        if row.get('language'):
            metas.append({
                "propertyUri": self.property_uris['language'],
                "value": row['language'].strip(),
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            })

        # Temporal coverage (multilingual)
        if row.get('temporal'):
            lang_parts = self.parse_multilingual_field(row['temporal'])
            for part in lang_parts:
                meta = {
                    "propertyUri": self.property_uris['temporal'],
                    "value": part['value'],
                    "typeUri": "http://www.w3.org/2001/XMLSchema#string"
                }
                if part['lang']:
                    meta['lang'] = part['lang']
                metas.append(meta)

        # Spatial coverage (multilingual)
        if row.get('spatial'):
            lang_parts = self.parse_multilingual_field(row['spatial'])
            for part in lang_parts:
                meta = {
                    "propertyUri": self.property_uris['spatial'],
                    "value": part['value'],
                    "typeUri": "http://www.w3.org/2001/XMLSchema#string"
                }
                if part['lang']:
                    meta['lang'] = part['lang']
                metas.append(meta)

        # Access Rights
        if row.get('accessRights'):
            metas.append({
                "propertyUri": self.property_uris['accessRights'],
                "value": row['accessRights'].strip(),
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            })

        # Identifier
        if row.get('identifier'):
            metas.append({
                "propertyUri": self.property_uris['identifier'],
                "value": row['identifier'].strip(),
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            })

        return metas

    def validate_dataset(self, dataset: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate dataset has required fields for publication

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        if dataset.get('status') == 'published':
            # Check 5 mandatory fields
            required_uris = [
                self.property_uris['title'],
                self.property_uris['type'],
                self.property_uris['creator'],
                self.property_uris['created'],
                self.property_uris['license']
            ]

            metas = dataset.get('metas', [])
            found_uris = set([m['propertyUri'] for m in metas])

            for uri in required_uris:
                if uri not in found_uris:
                    field_name = [k for k, v in self.property_uris.items() if v == uri][0]
                    errors.append(f"Missing required field for published status: {field_name}")

            # Check type is full COAR URI
            type_metas = [m for m in metas if m['propertyUri'] == self.property_uris['type']]
            if type_metas:
                type_value = type_metas[0]['value']
                if not type_value.startswith('http://'):
                    errors.append(f"Type must be full COAR URI, not '{type_value}'")

        return (len(errors) == 0, errors)
