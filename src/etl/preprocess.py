"""Preprocess module: Clean and repair raw JSON data before parsing."""

import re
import json
import logging
from typing import Tuple
from word2number import w2n

logger = logging.getLogger(__name__)


def try_convert_number_word(word: str) -> str:
    """Convert English number word to digit using word2number library."""
    if not word:
        return word
    
    word_lower = word.lower()
    
    if w2n:
        try:
            result = w2n.word_to_num(word_lower)
            return str(int(result))
        except (ValueError, TypeError, Exception):
            pass
    
    return word


def repair_bareword_values(raw_json_str: str) -> Tuple[str, list]:
    """Repair common bareword issues in JSON."""
    fixes = []
    repaired = raw_json_str
    
    # Pattern: barewords after colon
    pattern_bareword = r':\s*([A-Z][a-zA-Z]*)\s*([,\}])'
    
    def fix_any_bareword(match):
        bareword = match.group(1)
        delimiter = match.group(2)
        
        if bareword.lower() in {'true', 'false', 'null'}:
            return match.group(0)
        
        converted = try_convert_number_word(bareword)
        
        if converted != bareword and converted.isdigit():
            fixes.append(f"Converted number word to digit: {bareword} → {converted}")
            return f': {converted}{delimiter}'
        
        fixes.append(f"Quoted bareword: {bareword}")
        return f': "{bareword}"{delimiter}'
    
    repaired = re.sub(pattern_bareword, fix_any_bareword, repaired)
    
    # Pattern: number with trailing unit
    pattern_number_unit = r':\s*(\d+(?:\.\d+)?)\s+([a-z]+)\s*([,\}])'
    
    def fix_number_unit(match):
        number = match.group(1)
        unit = match.group(2)
        fixes.append(f"Quoted number with unit: {number} {unit}")
        return f': "{number} {unit}"{match.group(3)}'
    
    repaired = re.sub(pattern_number_unit, fix_number_unit, repaired)
    
    # Pattern: trailing commas
    pattern_trailing_comma = r',\s*([\}\]])'
    
    def fix_trailing_comma(match):
        fixes.append(f"Removed trailing comma before {match.group(1)}")
        return match.group(1)
    
    repaired = re.sub(pattern_trailing_comma, fix_trailing_comma, repaired)
    
    # Pattern: unquoted keys
    pattern_unquoted_key = r'\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:'
    
    def fix_unquoted_key(match):
        key = match.group(1)
        fixes.append(f"Quoted unquoted key: {key}")
        return f'{{""{key}":'
    
    repaired = re.sub(pattern_unquoted_key, fix_unquoted_key, repaired)
    
    # Pattern: bare numbers in objects
    pattern_bare_number_in_object = r',\s*(\d+)\s*([,\}])'
    
    def fix_bare_number(match):
        number = match.group(1)
        fixes.append(f"Removed bare number in object: {number}")
        return match.group(2)
    
    repaired = re.sub(pattern_bare_number_in_object, fix_bare_number, repaired)
    
    return repaired, fixes


def preprocess_json_string(raw_json_str: str, verbose: bool = False) -> Tuple[str, dict]:
    """Apply all preprocessing and repair steps to raw JSON string."""
    summary = {
        "original_length": len(raw_json_str),
        "fixes_applied": [],
        "success": False,
        "error_line": None,
        "error_context": None
    }
    
    logger.info("Starting JSON preprocessing...")
    
    cleaned, bareword_fixes = repair_bareword_values(raw_json_str)
    if bareword_fixes:
        logger.warning(f"Applied {len(bareword_fixes)} bareword repairs:")
        for fix in bareword_fixes[:5]:
            logger.warning(f"  - {fix}")
        if len(bareword_fixes) > 5:
            logger.warning(f"  ... and {len(bareword_fixes) - 5} more")
        summary["fixes_applied"].extend(bareword_fixes)
    
    summary["cleaned_length"] = len(cleaned)
    summary["fixes_count"] = len(bareword_fixes)
    
    try:
        json.loads(cleaned)
        summary["success"] = True
        logger.info(f"Preprocessing complete: {len(bareword_fixes)} fixes applied (JSON valid)")
    except json.JSONDecodeError as e:
        logger.warning(f"JSON still invalid after preprocessing: {e}")
        summary["error_line"] = e.lineno
        summary["error_col"] = e.colno
        summary["error_msg"] = str(e)
        
        lines = cleaned.split('\n')
        start = max(0, e.lineno - 2)
        end = min(len(lines), e.lineno + 1)
        context_lines = []
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            context_lines.append(f"{marker}Line {i+1}: {lines[i][:100]}")
        summary["error_context"] = "\n".join(context_lines)
        logger.error(f"Error context:\n{summary['error_context']}")
        summary["success"] = False
    
    return cleaned, summary


def load_and_preprocess_json(json_file_path: str) -> Tuple[str, dict]:
    """Load raw JSON file and apply preprocessing without modifying the file."""
    logger.info(f"Loading raw JSON from: {json_file_path}")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_json_str = f.read()
    except FileNotFoundError:
        logger.error(f"JSON file not found: {json_file_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to read JSON file: {e}")
        raise
    
    logger.info(f"Raw JSON loaded: {len(raw_json_str)} bytes")
    
    cleaned_json_str, summary = preprocess_json_string(raw_json_str, verbose=True)
    
    if summary["fixes_count"] > 0:
        logger.info(f"JSON repaired: {summary['fixes_count']} issues fixed")
    
    return cleaned_json_str, summary
