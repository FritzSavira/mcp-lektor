"""
Utilities for validating OpenXML (.docx) files.
Focuses on well-formedness and schema compliance.
"""

from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from lxml import etree

logger = logging.getLogger(__name__)

def validate_docx_structure(file_path: str | Path) -> bool:
    """
    Check if the .docx file is a valid ZIP and contains well-formed XML.
    Returns True if valid, raises ValueError or etree.XMLSyntaxError otherwise.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        with zipfile.ZipFile(path, 'r') as zf:
            # List of critical XML files to check
            critical_files = [
                'word/document.xml',
                'word/_rels/document.xml.rels',
                '[Content_Types].xml',
                '_rels/.rels'
            ]
            
            for xml_file in critical_files:
                if xml_file in zf.namelist():
                    with zf.open(xml_file) as f:
                        # Attempt to parse to check for well-formedness
                        etree.parse(f)
                else:
                    if xml_file == 'word/document.xml':
                        raise ValueError(f"Missing critical file in docx: {xml_file}")
            
            # Optional: Check comments if they exist
            if 'word/comments.xml' in zf.namelist():
                with zf.open('word/comments.xml') as f:
                    etree.parse(f)
                    
        return True
    except zipfile.BadZipFile:
        logger.error(f"File is not a valid ZIP: {path}")
        raise ValueError(f"Invalid .docx (not a ZIP): {path}")
    except etree.XMLSyntaxError as e:
        logger.error(f"XML Syntax Error in {path}: {e}")
        raise

def validate_word_xml_schema(xml_content: bytes) -> bool:
    """
    Placeholder for full XSD validation. 
    In a production environment, this would load the OOXML schemas.
    """
    try:
        etree.fromstring(xml_content)
        return True
    except etree.XMLSyntaxError:
        return False
