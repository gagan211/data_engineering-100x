"""Main ETL orchestration script."""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.etl.config import DatabaseConfig, ETLConfig
from src.etl.extract import load_properties_from_json
from src.etl.transform import transform_properties
from src.etl.load import load_to_database


def setup_logging(log_level: str = "INFO"):
    """Configure logging for ETL pipeline."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('etl_pipeline.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


logger = logging.getLogger(__name__)


def run_etl():
    """Execute complete ETL pipeline."""
    setup_logging(ETLConfig.LOG_LEVEL)
    
    logger.info("=" * 80)
    logger.info("DATA ENGINEERING ASSESSMENT: ETL PIPELINE")
    logger.info("=" * 80)
    
    logger.info("Configuration loaded:")
    for key, value in ETLConfig.to_dict().items():
        logger.info(f"  {key}: {value}")
    for key, value in DatabaseConfig.to_dict().items():
        if key != "password":
            logger.info(f"  db_{key}: {value}")
        else:
            logger.info(f"  db_{key}: ****")
    
    try:
        # STEP 1: EXTRACT
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1: EXTRACT - Loading and validating properties from JSON")
        logger.info("=" * 80)
        
        max_records = ETLConfig.MAX_RECORDS if ETLConfig.MAX_RECORDS > 0 else None
        valid_properties, invalid_records = load_properties_from_json(
            json_file_path=ETLConfig.JSON_INPUT_FILE,
            max_records=max_records,
            skip_invalid=ETLConfig.SKIP_INVALID
        )
        
        logger.info(f"\nExtract Summary:")
        logger.info(f"   Valid properties: {len(valid_properties)}")
        logger.info(f"  ✗ Invalid records: {len(invalid_records)}")
        
        if invalid_records and len(invalid_records) <= 5:
            logger.warning("Invalid record details:")
            for invalid in invalid_records[:5]:
                logger.warning(f"  Record {invalid['record_index']}: {invalid['errors'][0]}")
        
        if not valid_properties:
            logger.error("No valid properties to process. Exiting.")
            return False
        
        # STEP 2: TRANSFORM
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: TRANSFORM - Normalizing property data")
        logger.info("=" * 80)
        
        facts, dimensions = transform_properties(valid_properties)
        
        logger.info(f"\nTransform Summary:")
        logger.info(f"   Properties fact table: {len(facts['properties'])} rows")
        logger.info(f"   Valuations fact table: {len(facts['valuations'])} rows")
        logger.info(f"   HOA fees fact table: {len(facts['hoa_fees'])} rows")
        logger.info(f"   Rehab assessments fact table: {len(facts['rehab_assessments'])} rows")
        
        logger.info(f"\nDimension Summary:")
        logger.info(f"   Unique markets: {len(dimensions['markets'])}")
        logger.info(f"   Unique sources: {len(dimensions['sources'])}")
        logger.info(f"   Unique property types: {len(dimensions['property_types'])}")
        logger.info(f"   Unique layouts: {len(dimensions['layouts'])}")
        
        # STEP 3: LOAD
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: LOAD - Loading data into MySQL database")
        logger.info("=" * 80)
        
        load_to_database(
            host=DatabaseConfig.HOST,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASSWORD,
            database=DatabaseConfig.DATABASE,
            facts=facts,
            sql_init_file=ETLConfig.SQL_SCHEMA_FILE
        )
        
        logger.info(f"\nLoad Summary:  All data successfully loaded")
        
        # FINAL SUMMARY
        logger.info("\n" + "=" * 80)
        logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"\nFinal Statistics:")
        logger.info(f"  Total properties processed: {len(valid_properties)}")
        logger.info(f"  Total valuation snapshots: {len(facts['valuations'])}")
        logger.info(f"  Total HOA records: {len(facts['hoa_fees'])}")
        logger.info(f"  Total rehab assessments: {len(facts['rehab_assessments'])}")
        logger.info(f"\nDatabase: {DatabaseConfig.DATABASE}")
        logger.info(f"Host: {DatabaseConfig.HOST}:{DatabaseConfig.PORT}")
        logger.info(f"\nLog file: etl_pipeline.log")
        
        return True
    
    except Exception as e:
        logger.exception(f"ETL pipeline failed with error: {e}")
        return False


if __name__ == "__main__":
    success = run_etl()
    sys.exit(0 if success else 1)
