-- Hot Parts Database Schema
-- SQLite database for managing hot parts and excess inventory data

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Hot Parts Data (from weekly hot parts lists)
CREATE TABLE IF NOT EXISTS hot_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mpn TEXT NOT NULL,
    date TEXT NOT NULL,
    reqs_count INTEGER,
    manufacturer TEXT,
    product_class TEXT,
    description TEXT,
    source_file TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mpn, date, source_file)
);

-- Excess Inventory Data (from excess lists)
CREATE TABLE IF NOT EXISTS excess_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mpn TEXT NOT NULL,
    excess_filename TEXT NOT NULL,
    excess_qty INTEGER,
    target_price DECIMAL(10,2),
    manufacturer TEXT,
    sheet_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mpn, excess_filename, sheet_name)
);

-- Matches (cross-reference results between hot parts and excess)
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mpn TEXT NOT NULL,
    hot_parts_date TEXT,
    reqs_count INTEGER,
    manufacturer TEXT,
    product_class TEXT,
    description TEXT,
    excess_filename TEXT,
    excess_qty INTEGER,
    target_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Processing Log (track file processing history)
CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL, -- 'hot_parts' or 'excess'
    status TEXT NOT NULL, -- 'success', 'error', 'duplicate'
    records_processed INTEGER DEFAULT 0,
    records_added INTEGER DEFAULT 0,
    records_skipped INTEGER DEFAULT 0,
    error_message TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_hot_parts_mpn ON hot_parts(mpn);
CREATE INDEX IF NOT EXISTS idx_hot_parts_date ON hot_parts(date);
CREATE INDEX IF NOT EXISTS idx_hot_parts_manufacturer ON hot_parts(manufacturer);
CREATE INDEX IF NOT EXISTS idx_hot_parts_mpn_date ON hot_parts(mpn, date);

CREATE INDEX IF NOT EXISTS idx_excess_mpn ON excess_inventory(mpn);
CREATE INDEX IF NOT EXISTS idx_excess_filename ON excess_inventory(excess_filename);
CREATE INDEX IF NOT EXISTS idx_excess_manufacturer ON excess_inventory(manufacturer);

CREATE INDEX IF NOT EXISTS idx_matches_mpn ON matches(mpn);
CREATE INDEX IF NOT EXISTS idx_matches_manufacturer ON matches(manufacturer);
CREATE INDEX IF NOT EXISTS idx_matches_target_price ON matches(target_price);

CREATE INDEX IF NOT EXISTS idx_processing_log_filename ON processing_log(filename);
CREATE INDEX IF NOT EXISTS idx_processing_log_status ON processing_log(status);

-- Create views for common queries
CREATE VIEW IF NOT EXISTS v_hot_parts_summary AS
SELECT 
    mpn,
    manufacturer,
    COUNT(*) as total_occurrences,
    MIN(date) as first_seen,
    MAX(date) as last_seen,
    SUM(reqs_count) as total_reqs_count,
    AVG(reqs_count) as avg_reqs_count
FROM hot_parts
GROUP BY mpn, manufacturer;

CREATE VIEW IF NOT EXISTS v_excess_summary AS
SELECT 
    mpn,
    manufacturer,
    COUNT(*) as total_listings,
    SUM(excess_qty) as total_available_qty,
    AVG(target_price) as avg_target_price,
    MIN(target_price) as min_target_price,
    MAX(target_price) as max_target_price
FROM excess_inventory
GROUP BY mpn, manufacturer;

CREATE VIEW IF NOT EXISTS v_matches_summary AS
SELECT 
    mpn,
    manufacturer,
    COUNT(*) as total_matches,
    SUM(excess_qty) as total_available_qty,
    AVG(target_price) as avg_target_price,
    MIN(target_price) as min_target_price,
    MAX(target_price) as max_target_price
FROM matches
GROUP BY mpn, manufacturer;

-- Insert sample data for testing (optional)
-- INSERT INTO hot_parts (mpn, date, reqs_count, manufacturer, product_class, description, source_file) 
-- VALUES ('TEST123', '2025.07.07', 5, 'Test Manufacturer', 'Test Class', 'Test Description', 'test_file.xlsx');

-- INSERT INTO excess_inventory (mpn, excess_filename, excess_qty, target_price, manufacturer, sheet_name)
-- VALUES ('TEST123', 'test_excess.xlsx', 100, 15.50, 'Test Manufacturer', 'Raw Data'); 