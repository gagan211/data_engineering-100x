"""Configuration module for ETL pipeline."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent.parent


class DatabaseConfig:
    """Database connection settings."""
    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", "3306"))
    USER = os.getenv("DB_USER", "root")
    PASSWORD = os.getenv("DB_PASSWORD", "root")
    DATABASE = os.getenv("DB_NAME", "home_db")
    
    @classmethod
    def to_dict(cls):
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "user": cls.USER,
            "password": cls.PASSWORD,
            "database": cls.DATABASE
        }


class ETLConfig:
    """ETL pipeline settings."""
    JSON_INPUT_FILE = os.getenv("JSON_INPUT_FILE", str(BASE_DIR / "data" / "fake_property_data_new.json"))
    SQL_SCHEMA_FILE = os.getenv("SQL_SCHEMA_FILE", str(BASE_DIR / "sql" / "01_schema.sql"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
    MAX_RECORDS = int(os.getenv("MAX_RECORDS", "0"))  # 0 = no limit
    SKIP_INVALID = os.getenv("SKIP_INVALID", "true").lower() == "true"
    
    @classmethod
    def to_dict(cls):
        return {
            "json_input_file": cls.JSON_INPUT_FILE,
            "sql_schema_file": cls.SQL_SCHEMA_FILE,
            "log_level": cls.LOG_LEVEL,
            "batch_size": cls.BATCH_SIZE,
            "max_records": cls.MAX_RECORDS,
            "skip_invalid": cls.SKIP_INVALID
        }
