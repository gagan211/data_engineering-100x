# Data Engineering Assessment

Welcome!  
This exercise evaluates your core **data-engineering** skills:

| Competency | Focus                                                         |
| ---------- | ------------------------------------------------------------- |
| SQL        | relational modelling, normalisation, DDL/DML scripting        |
| Python ETL | data ingestion, cleaning, transformation, & loading (ELT/ETL) |

---

## 0 Prerequisites & Setup

> **Allowed technologies**

- **Python ≥ 3.8** – all ETL / data-processing code
- **MySQL 8** – the target relational database
- **Pydantic** – For data validation
- List every dependency in **`requirements.txt`** and justify selection of libraries in the submission notes.

---

## 1 Clone the skeleton repo

```
git clone https://github.com/100x-Home-LLC/data_engineer_assessment.git
```

✏️ Note: Rename the repo after cloning and add your full name.

**Start the MySQL database in Docker:**

```
docker-compose -f docker-compose.initial.yml up --build -d
```

- Database is available on `localhost:3306`
- Credentials/configuration are in the Docker Compose file
- **Do not change** database name or credentials

For MySQL Docker image reference:
[MySQL Docker Hub](https://hub.docker.com/_/mysql)

---

### Problem

- You are provided with a raw JSON file containing property records is located in data/
- Each row relates to a property. Each row mixes many unrelated attributes (property details, HOA data, rehab estimates, valuations, etc.).
- There are multiple Columns related to this property.
- The database is not normalized and lacks relational structure.
- Use the supplied Field Config.xlsx (in data/) to understand business semantics.

### Task

- **Normalize the data:**

  - Develop a Python ETL script to read, clean, transform, and load data into your normalized MySQL tables.
  - Refer the field config document for the relation of business logic
  - Use primary keys and foreign keys to properly capture relationships

- **Deliverable:**
  - Write necessary python and sql scripts
  - Place your scripts in `src/`
  - The scripts should take the initial json to your final, normalized schema when executed
  - Clearly document how to run your script, dependencies, and how it integrates with your database.

---

## Submission Guidelines

- Edit the section to the bottom of this README with your solutions and instructions for each section at the bottom.
- Ensure all steps are fully **reproducible** using your documentation
- DO NOT MAKE THE REPOSITORY PUBLIC. ANY CANDIDATE WHO DOES IT WILL BE AUTO REJECTED.
- Create a new private repo and invite the reviewer https://github.com/mantreshjain and https://github.com/siddhuorama

---

**Good luck! We look forward to your submission.**

---

# Solution

## Quick Start

```bash
# 1. Start MySQL
docker-compose -f docker-compose.initial.yml up --build -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run ETL
python src/etl/run_etl.py
```

---

## Overview

This solution normalizes a denormalized property JSON dataset (10,000+ records) into a relational MySQL 8 schema. The pipeline:

1. **Preprocesses** malformed JSON (handles bareword values, number words like "Four")
2. **Validates** data using Pydantic models
3. **Transforms** denormalized records into 4 normalized tables
4. **Loads** data into MySQL with proper FK relationships

**Final Results:**
- 10,088 properties loaded
- 24,898 valuation records
- 10,100 HOA fee records
- 20,219 rehab assessment records

---

## Project Structure

```
data_engineer_assessment/
├── src/
│   ├── models/
│   │   └── property.py          # Pydantic models for validation
│   └── etl/
│       ├── config.py            # Configuration (env vars)
│       ├── extract.py           # JSON loading + validation
│       ├── transform.py         # Normalization logic
│       ├── load.py              # MySQL database loader
│       ├── preprocess.py        # JSON repair (malformed data)
│       └── run_etl.py           # Main entry point
├── sql/
│   └── 01_schema.sql            # DDL for 4 tables
├── data/
│   └── fake_property_data_new.json
├── requirements.txt
└── README.md
```

---

## Database Schema

```
┌─────────────────────┐
│     properties      │  (PK: property_id)
└──────────┬──────────┘
           │
    ┌──────┼──────┬──────────────┐
    │      │      │              │
    ▼      ▼      ▼              ▼
┌─────────┐ ┌────────┐ ┌──────────────────┐
│valuations│ │hoa_fees│ │rehab_assessments │
└─────────┘ └────────┘ └──────────────────┘
   (FK)        (FK)           (FK)
```

### Tables

| Table | Description | Columns |
|-------|-------------|---------|
| `properties` | Core property data | property_id, address, city, state, zip, lat/lng, beds, baths, sqft, etc. |
| `valuations` | Property value estimates | source_name, estimate, rent_estimate, quality_score, valuation_date |
| `hoa_fees` | HOA information | hoa_name, monthly_fee, special_assessment, covers_* flags |
| `rehab_assessments` | Rehab cost estimates | roof/hvac/foundation/exterior/interior condition & costs |

---

## Setup Instructions

### Step 1: Start MySQL Container

```bash
docker-compose -f docker-compose.initial.yml up --build -d
```

Verify it's running:
```bash
docker ps | grep mysql
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**

| Package | Purpose |
|---------|---------|
| pydantic | Data validation with type hints |
| mysql-connector-python | MySQL database driver |
| word2number | Convert "Four" → 4 in malformed JSON |
| python-dotenv | Environment variable management |

### Step 3: Run the ETL Pipeline

```bash
python src/etl/run_etl.py
```

**Expected Output:**
```
================================================================================
DATA ENGINEERING ASSESSMENT: ETL PIPELINE
================================================================================
STEP 1: EXTRACT - Loading and validating properties from JSON
  ✓ Valid properties: 10088
  ✗ Invalid records: 0

STEP 2: TRANSFORM - Normalizing property data
  ✓ Properties fact table: 10088 rows
  ✓ Valuations fact table: 24898 rows
  ✓ HOA fees fact table: 10100 rows
  ✓ Rehab assessments fact table: 20219 rows

STEP 3: LOAD - Loading data into MySQL database
  ✓ All data successfully loaded

ETL PIPELINE COMPLETED SUCCESSFULLY
```

---

## Verify Data

Connect to MySQL:
```bash
mysql -h localhost -P 3306 -u root -proot home_db
```

Run verification queries:
```sql
-- Record counts
SELECT 'properties' as tbl, COUNT(*) as cnt FROM properties
UNION ALL SELECT 'valuations', COUNT(*) FROM valuations
UNION ALL SELECT 'hoa_fees', COUNT(*) FROM hoa_fees
UNION ALL SELECT 'rehab_assessments', COUNT(*) FROM rehab_assessments;

-- Sample property with related data
SELECT p.property_id, p.address, p.city, p.state
FROM properties p LIMIT 5;

-- Valuations for a property
SELECT v.* FROM valuations v
JOIN properties p ON v.property_id = p.property_id
LIMIT 10;
```

---

## Configuration

Default configuration uses environment variables with fallbacks:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | MySQL host |
| `DB_PORT` | 3306 | MySQL port |
| `DB_USER` | root | MySQL user |
| `DB_PASSWORD` | root | MySQL password |
| `DB_NAME` | home_db | Database name |
| `MAX_RECORDS` | 0 | Limit records (0 = all) |
| `SKIP_INVALID` | true | Skip invalid records |
| `LOG_LEVEL` | INFO | Logging verbosity |

Override via environment:
```bash
DB_HOST=myhost DB_USER=myuser python src/etl/run_etl.py
```

---

## ETL Pipeline Details

### Extract Phase
- Loads raw JSON from `data/fake_property_data_new.json`
- **Preprocesses** malformed JSON:
  - Converts number words ("Four" → 4) using word2number
  - Removes bare numbers in objects (invalid JSON syntax)
  - Fixes trailing commas
- Validates each record using Pydantic models
- Logs invalid records but continues processing

### Transform Phase
- Splits denormalized records into 4 normalized tables
- Extracts nested arrays (Valuation[], HOA[], Rehab[])
- Maintains property_id foreign key relationships
- Extracts dimension values (markets, sources, property types)

### Load Phase
- Executes DDL from `sql/01_schema.sql` (drops & recreates tables)
- Batch inserts using `executemany()` for performance
- Proper FK constraint handling (properties first, then related tables)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Can't connect to MySQL` | Run `docker-compose -f docker-compose.initial.yml up -d` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `JSONDecodeError` | Preprocessor should handle this; check logs |
| `Duplicate entry` | Schema drops tables on each run; re-run ETL |

Enable debug logging:
```bash
LOG_LEVEL=DEBUG python src/etl/run_etl.py
```

Check log file:
```bash
cat etl_pipeline.log
```

---

## Files Summary

| File | Purpose |
|------|---------|
| `src/etl/run_etl.py` | Main entry point - orchestrates Extract→Transform→Load |
| `src/etl/extract.py` | Loads JSON, preprocesses, validates with Pydantic |
| `src/etl/transform.py` | Normalizes data into 4 fact tables |
| `src/etl/load.py` | MySQL connection and insert operations |
| `src/etl/preprocess.py` | JSON repair for malformed data |
| `src/etl/config.py` | Configuration from environment variables |
| `src/models/property.py` | Pydantic models (Property, Valuation, HOA, Rehab) |
| `sql/01_schema.sql` | DDL for creating normalized tables |
