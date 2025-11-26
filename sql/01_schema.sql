-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS rehab_assessments;
DROP TABLE IF EXISTS hoa_fees;
DROP TABLE IF EXISTS valuations;
DROP TABLE IF EXISTS properties;

-- Main properties table
CREATE TABLE properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id VARCHAR(100) NOT NULL,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(255),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    num_units INT,
    floors INT,
    year_built INT,
    beds INT,
    full_baths INT,
    three_qtr_baths INT,
    half_baths INT,
    total_baths DECIMAL(5, 2),
    sqft INT,
    lot_size INT,
    property_type VARCHAR(100),
    layout VARCHAR(100),
    market VARCHAR(255),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_property_id (property_id)
);

-- Valuations (time series data)
CREATE TABLE valuations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id VARCHAR(100) NOT NULL,
    source_name VARCHAR(100),
    estimate DECIMAL(15, 2),
    rent_estimate DECIMAL(10, 2),
    quality_score INT,
    valuation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_property_id (property_id),
    INDEX idx_source (source_name),
    INDEX idx_valuation_date (valuation_date)
);

-- HOA fees
CREATE TABLE hoa_fees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id VARCHAR(100) NOT NULL,
    hoa_name VARCHAR(255),
    monthly_fee DECIMAL(10, 2),
    special_assessment DECIMAL(10, 2),
    covers_water BOOLEAN DEFAULT FALSE,
    covers_trash BOOLEAN DEFAULT FALSE,
    covers_pool BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_property_id (property_id)
);

-- Rehab assessments
CREATE TABLE rehab_assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id VARCHAR(100) NOT NULL,
    roof_condition VARCHAR(50),
    roof_cost DECIMAL(10, 2),
    hvac_condition VARCHAR(50),
    hvac_cost DECIMAL(10, 2),
    foundation_condition VARCHAR(50),
    foundation_cost DECIMAL(10, 2),
    exterior_condition VARCHAR(50),
    exterior_cost DECIMAL(10, 2),
    interior_condition VARCHAR(50),
    interior_cost DECIMAL(10, 2),
    total_rehab_cost DECIMAL(12, 2),
    assessment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_property_id (property_id),
    INDEX idx_assessment_date (assessment_date)
);

-- Foreign key constraints
ALTER TABLE valuations ADD CONSTRAINT fk_valuations_property FOREIGN KEY (property_id) REFERENCES properties(property_id);
ALTER TABLE hoa_fees ADD CONSTRAINT fk_hoa_property FOREIGN KEY (property_id) REFERENCES properties(property_id);
ALTER TABLE rehab_assessments ADD CONSTRAINT fk_rehab_property FOREIGN KEY (property_id) REFERENCES properties(property_id);
