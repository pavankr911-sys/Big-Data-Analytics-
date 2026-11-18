-- ==============================================================================
-- BCS714D Big Data Analytics - Theme 3: Apache Hive Tables Setup (Text vs RCFile)
-- Script: setup_tables.hql
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS energy_analytics_hive;
USE energy_analytics_hive;

-- 1. Create Standard Text Format Table
DROP TABLE IF EXISTS energy_text;
CREATE TABLE energy_text (
    country STRING,
    year INT,
    iso_code STRING,
    total_energy_twh DOUBLE,
    renewables_energy_twh DOUBLE,
    solar_electricity_twh DOUBLE,
    wind_electricity_twh DOUBLE,
    carbon_intensity DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

-- 2. Create Record Columnar File (RCFile) Format Table
DROP TABLE IF EXISTS energy_rcfile;
CREATE TABLE energy_rcfile (
    country STRING,
    year INT,
    iso_code STRING,
    total_energy_twh DOUBLE,
    renewables_energy_twh DOUBLE,
    solar_electricity_twh DOUBLE,
    wind_electricity_twh DOUBLE,
    carbon_intensity DOUBLE
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.columnar.ColumnarSerDe'
STORED AS RCFILE;

-- 3. Ingestion: Load data into Text table and populate RCFile table
-- Note: Set hive.exec.compress.output=true to leverage RCFile block compression
SET hive.exec.compress.output=true;
SET mapreduce.output.fileoutputformat.compress=true;
SET mapreduce.output.fileoutputformat.compress.codec=org.apache.hadoop.io.compress.GzipCodec;

LOAD DATA INPATH '${hiveconf:PIG_OUTPUT_PATH}' OVERWRITE INTO TABLE energy_text;

INSERT OVERWRITE TABLE energy_rcfile
SELECT 
    country,
    year,
    iso_code,
    total_energy_twh,
    renewables_energy_twh,
    solar_electricity_twh,
    wind_electricity_twh,
    carbon_intensity
FROM energy_text;

