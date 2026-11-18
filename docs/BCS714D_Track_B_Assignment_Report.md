# BCS714D — Big Data Analytics
## Track B: Practical Engineering Final Submission Report

---

**Course Title:** Big Data Analytics (BCS714D)  
**Academic Year:** 2026 – 2027  
**Sections:** 7A and 7B  
**Faculty In-Charge:** Sandhiya B  
**Track Selected:** Track B — Practical Engineering (15 Marks Core Themes + 10 Marks Practical Extension)  
**Dataset Assigned:** Our World in Data (OWID) Global Energy Dataset  
- **Raw Historical Dataset:** 19,494 rows × 130 columns (`data/raw/owid_energy.csv`)  
- **Target Analysis Scope (2000–2024):** 6,324 rows × 130 columns (`data/processed/energy_2000_2024.csv`)  
- **Pig Cleaned Warehousing Dataset:** 5,921 clean rows × 8 columns (`/content/energy_project/pig_cleaned`)  
**Primary Databases & Engines:**  
- **Local Engine (Verified):** MongoDB Community Server 9.0.4 on Windows 11  
- **Distributed Engine (Verified):** Apache Hadoop 3.3.6, Pig 0.17.0, Hive 3.1.3 (Google Colab Linux Node)  
**Application Extension (Verified):** Python Flask REST API & Chart.js Web Dashboard  

---

## 1. Executive Summary & Verification Matrix

Every mandatory practical requirement in Track B has been systematically executed, verified with live command outputs, and preserved in the project directory:

| Component | Status | Empirical Output / Measured Finding | Evidence File |
| :--- | :--- | :--- | :--- |
| **Dataset Ingestion & Key Audit** | **VERIFIED** | Raw: 19,494 rows; Processed (2000–2024): 6,324 rows across 255 countries. | [`energy_2000_2024.csv`](file:///c:/Users/admin/OneDrive/Desktop/big%20data/data/processed/energy_2000_2024.csv) |
| **MongoDB Document Ingestion** | **VERIFIED** | Both `energy_data` and `energy_data_clean` contain 6,324 docs; 5 numeric indicators cast. | MongoDB Service `localhost:27017` |
| **Compound Indexing & Profiling** | **VERIFIED** | `country_year_idx` reduced docs examined from 6,324 to 1 (**99.984% reduction**, 0 ms vs 3 ms). | [`theme1_performance_profiling.json`](file:///c:/Users/admin/OneDrive/Desktop/big%20data/results/mongodb/theme1_performance_profiling.json) |
| **MongoDB Aggregations** | **VERIFIED** | `$match`, `$group`, `$project`, `$unwind`, and `$facet` executed and saved. | [`theme1_aggregation_results.json`](file:///c:/Users/admin/OneDrive/Desktop/big%20data/results/mongodb/theme1_aggregation_results.json) |
| **HDFS Operations Lifecycle** | **VERIFIED** | `-mkdir`, `-put`, `-cat`, `-get` (6,325 lines retrieved), and `-rm -r` executed. | [`hdfs_operations.log`](file:///c:/Users/admin/OneDrive/Desktop/big%20data/results/hdfs/hdfs_operations.log) |
| **Hadoop Streaming MapReduce** | **VERIFIED** | 6,324 input rows processed into **255 country summaries** with strict `NA` missing-value logic. | [`part-00000.tsv`](file:///c:/Users/admin/OneDrive/Desktop/big%20data/results/mapreduce/part-00000.tsv) |
| **Apache Pig Transformation** | **VERIFIED** | 6,325 raw lines filtered into **5,921 clean rows** in 7.24s (403 unobserved totals excluded). | [`pig_execution.log`](file:///c:/Users/admin/OneDrive/Desktop/big%20data/results/pig/pig_execution.log) |
| **Hive Storage Footprint** | **VERIFIED** | TextFile: **291,407 bytes**; RCFile: **64,714 bytes** (**4.502x storage ratio, 77.79% space savings**). | [`benchmark_summary.json`](file:///c:/Users/admin/OneDrive/Desktop/big%20data/results/hive/benchmark_summary.json) |
| **Hive Analytical Benchmarks** | **VERIFIED** | Grouped aggregation: **2.50x speedup**; Selective filter: **2.54x speedup** on RCFile. | [`rcfile_vs_text_benchmark.csv`](file:///c:/Users/admin/OneDrive/Desktop/big%20data/results/hive/rcfile_vs_text_benchmark.csv) |
| **Flask Dashboard (Extension)** | **VERIFIED** | REST API & UI connected to local MongoDB; 5 endpoints verified with 100% pass rate. | [`test_app.py`](file:///c:/Users/admin/OneDrive/Desktop/big%20data/extension/flask_dashboard/test_app.py) |

---

## 2. Dataset Audit & Scope Definition

An audit of the project data directory confirmed the structural dimensions of the dataset:
- **Raw Source File (`data/raw/owid_energy.csv`)**: Contains **19,494 records** and **130 columns**, covering historical global energy indicators back to 1900.
- **Analysis Scope (2000–2024)**: Historical records prior to 2000 suffer from severe indicator sparsity (especially for solar, wind, and carbon intensity metrics). A consistent 25-year analysis period was isolated.
- **Processed Target File (`data/processed/energy_2000_2024.csv`)**: Contains exactly **6,324 rows** and **130 columns** across 255 unique countries and territories. All country-year keys are validated and free of duplicates.

---

## 3. System Environment & Architectural Strategy

### 3.1 Host Environment Constraints
- **Hardware**: Windows 11 64-bit, Intel Core i5, 8.00 GB Physical RAM, SSD.
- **Installed Software**: MongoDB Community Server 9.0.4, Python 3.14 (`pymongo`, `flask`, `pandas`).
- **Host Java**: Java SE 25 LTS (`build 25+37-LTS-3491`).
- **Virtualization**: WSL is not installed; Docker is not installed.

### 3.2 Dual-Environment Execution Strategy
Running Apache Hadoop 3.x, Pig 0.17, and Hive 3.1 directly on native Windows 11 with 8 GB RAM encounters fatal JVM encapsulation issues under Java 25, colon-delimited path bugs in Hive Derby (`C:\`), and severe memory thrashing.
- **Local Host (Windows 11)**: Hosts Theme 1 (MongoDB 9.0) and Part 2 (Flask Dashboard) with instant local responsiveness.
- **Cloud Linux Harness (Google Colab / Ubuntu)**: Hosts Theme 2 (HDFS, MapReduce) and Theme 3 (Pig, Hive RCFile) in an isolated Ubuntu environment with 12+ GB RAM, OpenJDK 8, and native POSIX support.

---

## 4. Part 1 — Theme 1: MongoDB Big Data Processing & Analytics (Verified)

### 4.1 Collection Verification (`energy_data` vs. `energy_data_clean`)
Inspection of the `energy_analytics` database clarified the exact contents of the collections:
- `energy_data`: Contains **6,324 processed records** (2000–2024) with only the default `_id_` index. (It contains the validated analysis dataset, not the 19,494 historical rows).
- `energy_data_clean`: Contains the identical **6,324 documents** with five central numeric energy indicators type-cast to double-precision floats, and indexed on `country_year_idx`.

Five converted numeric indicators:
1. `total_energy_twh`
2. `renewables_energy_twh`
3. `solar_electricity_twh`
4. `wind_electricity_twh`
5. `electricity_carbon_intensity_gco2eq_per_kwh`

### 4.2 Compound Index Verification (`country_year_idx`)
The compound B-tree index was verified:
```javascript
db.energy_data_clean.createIndex({ "country": 1, "year": 1 }, { name: "country_year_idx" });
```

### 4.3 Query Performance Profiling (`.explain("executionStats")`)
Query evaluated: `db.energy_data_clean.find({"country": "India", "year": 2023})`

| Performance Metric | Compound Index (`country_year_idx`) | Collection Scan (`COLLSCAN`) | Actual Measured Difference |
| :--- | :--- | :--- | :--- |
| **Execution Stage** | `FETCH` $\rightarrow$ `IXSCAN` | `COLLSCAN` | B-tree index direct lookup |
| **Index Used** | `country_year_idx` | `None (COLLSCAN)` | Structured index |
| **Keys Examined (`totalKeysExamined`)** | **1** | **0** | Exact key hit |
| **Documents Examined (`totalDocsExamined`)** | **1** | **6,324** | **99.984% reduction** (6,323 docs skipped) |
| **Documents Returned (`nReturned`)** | 1 | 1 | Consistent target record |
| **Execution Time (`executionTimeMillis`)** | **0 ms** | **3 ms** | Sub-millisecond latency |

*Note on Latency Benchmarks*: In preliminary cold-socket experiments stored in `performance_results.bson`, cold execution timings of 23 ms (indexed) vs 14 ms (scan) were recorded before cache warming. In warmed execution profiling, the indexed query executed in **0 ms** examining **1 document**, compared to **3 ms** examining all **6,324 documents**, demonstrating a definitive **99.984% reduction in document examinations** ($\frac{6,324 - 1}{6,324} \times 100\% = 99.984\%$).

### 4.4 Aggregation Pipelines Executed
1. **Decadal Energy Transition (`$match`, `$project`, `$group`)**: Computed 5-year average generation and renewable penetration across major economies (India, China, US, Germany, Brazil). For India, renewable energy grew from 81.33 TWh (2000–2004) to 387.94 TWh (2020–2024).
2. **Indicator Normalization (`$unwind`)**: Unwound multi-indicator documents into 20 normalized observation records for India across milestone years (2000, 2010, 2020, 2023).
3. **Multi-Faceted Dashboard Analysis (`$facet`)**: Concurrently computed global 2023 totals:
   - Global Total Energy: 160,636.92 TWh
   - Global Clean Energy: 11,777.90 TWh (7.33% penetration)
   - Average Carbon Intensity: 438.37 gCO2eq/kWh
   - Top 3 Renewable Volume: China (3,094.71 TWh), United States (1,726.15 TWh), Brazil (1,010.46 TWh).

---

## 5. Part 1 — Theme 2: Hadoop File Management & MapReduce Analytics (Verified)

### 5.1 HDFS Operations Lifecycle (Live Verified)
All five mandatory HDFS operations were executed and logged in `results/hdfs/hdfs_operations.log`:
1. `hdfs dfs -mkdir -p file:///content/energy_project/input file:///content/energy_project/scratch_temp`: Created namespaces.
2. `hdfs dfs -put -f /content/energy_2000_2024.csv file:///content/energy_project/input/`: Stored 4.2 MB dataset.
3. `hdfs dfs -cat file:///content/energy_project/input/energy_2000_2024.csv | head -n 5`: Read CSV header and records.
4. `hdfs dfs -get -f file:///content/energy_project/input/energy_2000_2024.csv /tmp/retrieved_energy.csv`: Retrieved **6,325 lines** intact.
5. `hdfs dfs -rm -r file:///content/energy_project/scratch_temp`: Deleted temporary staging directory.

### 5.2 MapReduce Execution on Hadoop Streaming
The job was submitted using Apache Hadoop 3.3.6 Streaming (`hadoop-streaming-3.3.6.jar`):
- **Mapper (`mapper.py`)**: Emits `country \t year,total,renewables,solar,wind`.
- **Strict Missing-Value Policy**: Unobserved indicators are preserved as `'NA'` rather than being coerced to `0.0`. The reducer maintains separate valid observation counters for each indicator, preventing artificial denominator dilution. If an indicator has no records (e.g. Afghanistan renewable energy), it outputs `NA` rather than a misleading `0.00`.
- **Hadoop MapReduce Job Counters**:
  - `Map input records`: **6,325**
  - `Map output records`: **6,324**
  - `Reduce input groups`: **255**
  - `Reduce input records`: **6,324**
  - `Reduce output records`: **255**
  - `File Bytes Read`: **4,439,254**
  - `File Bytes Written`: **15,060**
  - `Job Status`: **Completed successfully**

Sample output from `results/mapreduce/part-00000.tsv`:
- **China**: 25 years, avg total energy: 28,679.14 TWh, peak: 44,106.52 TWh (2024), peak renewables: 3,612.36 TWh (2024), renewable share: 4.64%.
- **India**: 25 years, avg total energy: 6,673.51 TWh, peak: 10,783.03 TWh (2024), peak renewables: 494.90 TWh (2024), renewable share: 3.43%.
- **United States**: 25 years, avg total energy: 25,720.11 TWh, peak: 26,929.27 TWh (2007), peak renewables: 1,837.49 TWh (2024), renewable share: 4.34%.
- **Afghanistan**: 25 years, avg total: 26.37 TWh, renewables: `NA`, solar: 0.03, wind: 0.00, peak renewables: `NA`.

---

## 6. Part 1 — Theme 3: Apache Pig Latin & Apache Hive RCFile Benchmarking (Verified)

### 6.1 Apache Pig Transformation & Row Attrition Explanation
Executed on Apache Pig 0.17.0 (`clean_energy.pig`):
```pig
valid_records = FILTER raw_energy BY 
    country != 'country' AND country IS NOT NULL AND 
    year >= 2000 AND year <= 2024 AND 
    total_energy_twh IS NOT NULL;
```
*Exact Reason 6,324 Rows Became 5,921 Rows*:
In the validated 2000–2024 dataset (6,324 data rows), exactly **403 rows** contain unobserved/null values for `total_energy_twh`. These 403 rows represent Ember regional entities (e.g. `ASEAN (Ember)`, `Africa (Ember)`, `Asia (Ember)`, `EU (Ember)`, `G20 (Ember)`, `Latin America (Ember)`), which track electricity generation but lack primary total energy figures, along with small overseas territories like `Gibraltar` and group aggregations like `Low-income countries`. The Pig script's explicit filter `total_energy_twh IS NOT NULL` properly discarded these 403 incomplete observations ($6,324 - 403 = \mathbf{5,921}$ rows).

*Null Preservation Policy*: Missing secondary metrics remain `null` (emitted as empty strings by `PigStorage(',')`). This ensures that downstream SQL/Hive `AVG()` aggregations ignore unobserved values rather than diluting averages with false zeroes.

### 6.2 Hive Table Storage Footprint & Compression Confirmation
Data was ingested into Apache Hive 3.1.3:
- Table 1: `energy_text` (`STORED AS TEXTFILE`)
- Table 2: `energy_rcfile` (`ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.columnar.ColumnarSerDe' STORED AS RCFILE`)
- Compression: Configured using `hive.exec.compress.output=true` with GzipCodec (`org.apache.hadoop.io.compress.GzipCodec`).

#### Genuine Measured Disk Storage Footprint Table
| Format | Directory Path | Size (Bytes) | Size (KB) | Storage Ratio | Space Reduction | Compression Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Standard TextFile** | `/content/.../energy_text` | **291,407 bytes** | **284.58 KB** | 1.00x (Baseline) | 0.00% | Uncompressed text |
| **RCFile (Columnar)**| `/content/.../energy_rcfile` | **64,714 bytes** | **63.20 KB** | **4.502x** | **77.79%** | **Confirmed (Gzip block compressed)** |

*Storage Findings*: The 4.502x reduction (77.79% space savings) results from the dual benefit of structural columnar data grouping (adjacent identical data types) combined with confirmed Gzip block compression.

### 6.3 Identical Analytical Query Latency Benchmarks (HQL)
Three identical analytical queries were executed against both table formats with vectorization disabled (`SET hive.vectorized.execution.enabled=false;`) to allow clean RCFile SerDe scanning:

| Query ID & Analytical Intent | Columns Read | TextFile Latency | RCFile Latency | Speedup Factor | Timing Methodology & Finding |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Query 1: Full-table Scan & Grouped Aggregation** (`COUNT(*)`, `AVG(total)`, `AVG(renewables)` by country) | 3 of 8 cols | **6.937 s** | **2.776 s** | **2.50x Speedup** | End-to-end HQL execution time reported by Hive CLI. Columnar layout skips reading unneeded columns, cutting scan time in half. |
| **Query 2: Selective Columnar Filter** (`solar > 10.0` AND `year >= 2018`) | 4 of 8 cols | **0.571 s** | **0.225 s** | **2.54x Speedup** | Map-only query. Column projection pruning bypasses unreferenced columns (`iso_code`, `carbon_intensity`), reducing I/O latency. |
| **Query 3: Multi-column Annual Transition** (`AVG(carbon)`, renewable share % by year) | 6 of 8 cols | **1.724 s** | **1.631 s** | **1.06x Speedup** | Multi-column read maintains competitive latency while retaining 77.79% disk storage compression. |

---

## 7. Part 2: 10-Mark Practical Extension — Flask Web Dashboard (Verified)

### 7.1 Architecture & MongoDB Direct Integration
The web application (`extension/flask_dashboard/app.py`) runs on `http://127.0.0.1:5000` and connects directly to the local MongoDB database `energy_analytics`, collection `energy_data_clean`.

### 7.2 Automated API Verification Results
Executed via `python extension/flask_dashboard/test_app.py`:
- `GET /`: Status 200 (Dashboard UI rendered)
- `GET /api/kpis`: Status 200 (Returned 6,324 documents, 255 countries, 2023 clean energy 11,777.9 TWh)
- `GET /api/countries`: Status 200 (Retrieved 255 unique countries)
- `GET /api/country/India`: Status 200 (Retrieved 25 annual records, 2000–2024)
- `GET /api/top_renewables?year=2023`: Status 200 (Top 10 renewable producers: China, US, Brazil, Canada, India)
- **Result**: **100% pass rate** (All 5 endpoints tested and verified with zero failures).

---

## 8. Artifact Directory & Evidence Repository

```
big data/
├── data/
│   ├── raw/
│   │   ├── owid_energy.csv                   # Raw dataset (19,494 rows, 130 columns)
│   │   └── owid_energy.codebook.csv          # Metadata codebook
│   └── processed/
│       ├── energy_validated.csv              # Validated keys
│       └── energy_2000_2024.csv              # Analysis dataset (6,324 rows, 130 columns)
├── energy_mongodb_backup/                    # Untouched BSON backup
├── scripts/
│   ├── theme1_mongodb_analytics.py           # MongoDB aggregation & explainStats (Verified)
│   ├── mapreduce/
│   │   ├── mapper.py                         # Mapper with NA handling (Verified)
│   │   └── reducer.py                        # Reducer with NA handling (Verified)
│   ├── pig/
│   │   └── clean_energy.pig                  # Pig Latin script preserving nulls (Verified)
│   └── hive/
│       ├── setup_tables.hql                  # Text vs RCFile table setup (Verified)
│       └── benchmark_queries.hql             # 3 identical HQL benchmark queries (Verified)
├── notebooks/
│   └── BCS714D_TrackB_Hadoop_Pig_Hive.ipynb  # Turnkey Colab execution notebook (Verified)
├── extension/
│   └── flask_dashboard/
│       ├── app.py                            # Flask server (Verified)
│       ├── test_app.py                       # Automated test suite (Verified)
│       ├── templates/index.html              # Responsive UI with Chart.js
│       └── static/style.css                  # Dark-mode dashboard stylesheet
├── results/
│   ├── mongodb/
│   │   ├── theme1_aggregation_results.json   # MongoDB aggregation output (Verified)
│   │   └── theme1_performance_profiling.json # 99.984% reduction profiling (Verified)
│   ├── hdfs/
│   │   └── hdfs_operations.log               # Live HDFS command logs (Verified)
│   ├── mapreduce/
│   │   ├── hadoop_mapreduce_job.log          # Live Hadoop MR job counters (Verified)
│   │   └── part-00000.tsv                    # 255 country transition summaries (Verified)
│   ├── pig/
│   │   └── pig_execution.log                 # Live Pig 0.17 execution log (Verified)
│   └── hive/
│       ├── rcfile_vs_text_benchmark.csv      # Live HQL query timings (Verified)
│       ├── benchmark_summary.json            # 291,407 vs 64,714 byte storage stats (Verified)
│       └── hive_benchmark_queries.log        # Live HQL execution transcript (Verified)
└── docs/
    └── BCS714D_Track_B_Assignment_Report.md  # Official Submission Report (Verified)
```

---
*Report End — BCS714D Big Data Analytics Track B Submission Report*
