# Entity-Relationship Diagram (ERD)

## Database Schema Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       HOME_DB DATABASE                      │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │   PROPERTIES         │
                    │  (Fact Table)        │
                    ├──────────────────────┤
                    │ PK: property_id      │
                    │                      │
                    │ • Address            │
                    │ • Location (lat/lng) │
                    │ • Property Details   │
                    │ • Financial Metrics  │
                    │ • Market & Source    │
                    │ • Status Info        │
                    │                      │
                    │ 41 columns           │
                    └──────┬───────────────┘
                           │
           ┌───────────────┼───────────────┬──────────────────┐
           │               │               │                  │
           ▼               ▼               ▼                  ▼
    ┌──────────────┐ ┌──────────────┐ ┌────────────┐ ┌──────────────────┐
    │ VALUATIONS   │ │  HOA_FEES    │ │   REHAB    │ │  (Future Dims)   │
    │ (Fact Table) │ │ (Fact Table) │ │  ASSESS.   │ │   dim_market     │
    ├──────────────┤ ├──────────────┤ ├────────────┤ │   dim_source     │
    │ PK: val_id   │ │ PK: hoa_id   │ │ PK: re_id  │ │   dim_type       │
    │ FK: prop_id  │ │ FK: prop_id  │ │ FK: prop_id│ │                  │
    ├──────────────┤ ├──────────────┤ ├────────────┤ └──────────────────┘
    │ • List Price │ │ • HOA Amount │ │ • Costs    │
    │ • ARV        │ │ • HOA Flag   │ │ • Flags    │
    │ • Zestimate  │ │              │ │ (10 types) │
    │ • Rent Est.  │ │              │ │            │
    │ • FMR        │ │              │ │            │
    │ • Redfin     │ │              │ │            │
    │              │ │              │ │            │
    │ 9 columns    │ │ 2 columns    │ │ 15 columns │
    └──────────────┘ └──────────────┘ └────────────┘

    1:N             1:N                1:N
```

## Relationship Cardinality

| Parent | Child | Type | Notes |
|--------|-------|------|-------|
| properties | valuations | 1:N | One property has 1-5 valuation snapshots |
| properties | hoa_fees | 1:N | One property has 0-3 HOA fee records |
| properties | rehab_assessments | 1:N | One property has 1-2 rehab assessments |

## Constraints

### Primary Keys
- **properties:** `property_id` (auto-increment)
- **valuations:** `valuation_id` (auto-increment)
- **hoa_fees:** `hoa_id` (auto-increment)
- **rehab_assessments:** `rehab_id` (auto-increment)

### Foreign Keys
All child tables have FK to properties with `ON DELETE CASCADE`:
- **valuations.property_id** → properties.property_id
- **hoa_fees.property_id** → properties.property_id
- **rehab_assessments.property_id** → properties.property_id

### Indexes

**properties table:**
- Primary: `property_id`
- Unique: `uk_address_zip` (address, zip_code) — quasi-unique constraint
- Search: `idx_address`, `idx_market`, `idx_source`, `idx_property_type`
- Composite: `idx_city_state_zip` (city, state, zip_code)

**Child tables:**
- `idx_property_id` (FK lookup)
- Composite: `idx_property_id, index_col` (e.g., valuation_index)

## Normalization Strategy

### Before (Denormalized JSON)
```json
{
  "Property_Title": "...",
  "Address": "...",
  "Valuation": [
    { "List_Price": 100000, "ARV": 130000, ... },
    { "List_Price": 110000, "ARV": 135000, ... }
  ],
  "HOA": [
    { "HOA": 450, "HOA_Flag": "No" }
  ],
  "Rehab": [
    { "Underwriting_Rehab": 66402, "Foundation_Flag": "Yes", ... }
  ]
}
```

### After (Normalized)
```
properties table (1 row):
- property_id: 1
- property_title: "..."
- address: "..."
- ... (40 more columns)

valuations table (2 rows):
- valuation_id: 1, property_id: 1, list_price: 100000, ...
- valuation_id: 2, property_id: 1, list_price: 110000, ...

hoa_fees table (1 row):
- hoa_id: 1, property_id: 1, hoa_amount: 450, ...

rehab_assessments table (1 row):
- rehab_id: 1, property_id: 1, underwriting_rehab: 66402, ...
```

## Data Flow Visualization

```
                    fake_property_data_new.json (raw, denormalized)
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  PYDANTIC VALIDATION  │
                        │  - Type coercion      │
                        │  - Null normalization │
                        │  - Flag validation    │
                        └───────────┬───────────┘
                                    │
                                    ▼
                    List[Property] (validated objects)
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  TRANSFORMATION       │
                        │  - Denormalize        │
                        │  - Extract facts      │
                        │  - Extract dims       │
                        └───────────┬───────────┘
                                    │
                                    ▼
              Dict[table_name → List[row_dicts]]
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  DATABASE LOAD        │
                        │  - Create schema (DDL)│
                        │  - Insert facts (DML) │
                        └───────────┬───────────┘
                                    │
                                    ▼
                          home_db (MySQL 8)
                    ├─ properties (999 rows)
                    ├─ valuations (3000 rows)
                    ├─ hoa_fees (1200 rows)
                    └─ rehab_assessments (1000 rows)
```

## Query Patterns

### 1-to-N Lookups
```sql
-- Get all valuations for a property
SELECT * FROM valuations WHERE property_id = 42;

-- Get properties with multiple valuations
SELECT p.property_id, p.address, COUNT(v.valuation_id) as val_count
FROM properties p
JOIN valuations v ON p.property_id = v.property_id
GROUP BY p.property_id
HAVING val_count > 1;
```

### Aggregations Across Related Tables
```sql
-- Average valuation per market
SELECT p.market, AVG(v.list_price) as avg_price
FROM properties p
JOIN valuations v ON p.property_id = v.property_id
GROUP BY p.market;

-- Properties with HOA + rehab needs
SELECT p.property_id, p.address, h.hoa_amount, COUNT(r.rehab_id)
FROM properties p
LEFT JOIN hoa_fees h ON p.property_id = h.property_id
LEFT JOIN rehab_assessments r ON p.property_id = r.property_id
WHERE r.foundation_flag = 'YES' AND h.hoa_amount IS NOT NULL;
```
