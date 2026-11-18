-- ==============================================================================
-- BCS714D Big Data Analytics - Theme 3: Hive Performance Benchmark Queries
-- Comparing TextFile vs RCFile on identical analytical queries
-- Configured for standalone/local execution with vectorization disabled
-- ==============================================================================

USE energy_analytics_hive;
SET hive.exec.mode.local.auto=false;
SET mapreduce.framework.name=local;

-- Disable Hive 3 vectorizer to allow clean RCFile SerDe scanning
SET hive.vectorized.execution.enabled=false;
SET hive.vectorized.execution.reduce.enabled=false;

-- -----------------------------------------------------------------------------
-- Query 1: Full-table Scan & Grouped Aggregation
-- Purpose: Evaluates full dataset read throughput and reducer aggregation speed
-- -----------------------------------------------------------------------------
-- [1A] On Standard Text Table:
SELECT country, COUNT(*) as years, ROUND(AVG(total_energy_twh), 2) as avg_tot, ROUND(AVG(renewables_energy_twh), 2) as avg_ren
FROM energy_text GROUP BY country LIMIT 10;

-- [1B] On RCFile Table:
SELECT country, COUNT(*) as years, ROUND(AVG(total_energy_twh), 2) as avg_tot, ROUND(AVG(renewables_energy_twh), 2) as avg_ren
FROM energy_rcfile GROUP BY country LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 2: Selective Columnar Projection & Filter
-- Purpose: Tests RCFile column-pruning advantage (reads only 4 of 8 columns)
-- -----------------------------------------------------------------------------
-- [2A] On Standard Text Table:
SELECT country, year, solar_electricity_twh, wind_electricity_twh
FROM energy_text WHERE solar_electricity_twh > 10.0 AND year >= 2018 LIMIT 10;

-- [2B] On RCFile Table:
SELECT country, year, solar_electricity_twh, wind_electricity_twh
FROM energy_rcfile WHERE solar_electricity_twh > 10.0 AND year >= 2018 LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 3: Multi-column Arithmetic Metric & Temporal Trend
-- Purpose: Global annual renewable transition rate & carbon intensity correlation
-- -----------------------------------------------------------------------------
-- [3A] On Standard Text Table:
SELECT year, ROUND(AVG(carbon_intensity), 2) as avg_carbon, ROUND((SUM(renewables_energy_twh)/SUM(total_energy_twh))*100, 2) as ren_pct
FROM energy_text WHERE total_energy_twh > 0 GROUP BY year LIMIT 10;

-- [3B] On RCFile Table:
SELECT year, ROUND(AVG(carbon_intensity), 2) as avg_carbon, ROUND((SUM(renewables_energy_twh)/SUM(total_energy_twh))*100, 2) as ren_pct
FROM energy_rcfile WHERE total_energy_twh > 0 GROUP BY year LIMIT 10;
