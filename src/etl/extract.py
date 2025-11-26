"""Extract module: Load and validate JSON property data using Pydantic."""

import json
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any
from pydantic import ValidationError

from src.models import Property
from src.etl.preprocess import load_and_preprocess_json

logger = logging.getLogger(__name__)


def load_properties_from_json(
    json_file_path: str,
    max_records: int = None,
    skip_invalid: bool = True
) -> Tuple[List[Property], List[Dict[str, Any]]]:
    """Load and validate properties from JSON file."""
    json_file_path = Path(json_file_path)
    
    if not json_file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_file_path}")
    
    valid_properties = []
    invalid_records = []
    
    logger.info(f"Starting to load properties from {json_file_path}")
    
    # Preprocess JSON (repair common errors)
    logger.info("Step 1: Preprocessing JSON (repairing common syntax errors)...")
    try:
        cleaned_json_str, preprocess_summary = load_and_preprocess_json(json_file_path)
        logger.info(f"Preprocessing complete: {preprocess_summary['fixes_count']} repairs applied")
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise
    
    # Parse preprocessed JSON
    logger.info("Step 2: Parsing cleaned JSON...")
    try:
        raw_data = json.loads(cleaned_json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON after preprocessing: {e}")
        raise
    
    if not isinstance(raw_data, list):
        raw_data = [raw_data]
    
    total_records = len(raw_data)
    if max_records:
        raw_data = raw_data[:max_records]
        logger.info(f"Processing first {max_records} of {total_records} records")
    else:
        logger.info(f"Processing all {total_records} records")
    
    for idx, raw_record in enumerate(raw_data, 1):
        try:
            validated_property = Property.model_validate(raw_record)
            valid_properties.append(validated_property)
            
            if idx % 100 == 0:
                logger.debug(f"Processed {idx} records successfully")
                
        except ValidationError as e:
            logger.warning(f"Validation error at record {idx}: {e.error_count()} error(s)")
            invalid_records.append({
                "record_index": idx,
                "raw_record": raw_record,
                "errors": e.errors()
            })
            
            if not skip_invalid:
                raise
    
    logger.info(f"Load complete: {len(valid_properties)} valid, {len(invalid_records)} invalid")
    
    return valid_properties, invalid_records
