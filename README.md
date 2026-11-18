# BCS714D — Big Data Analytics (Track B: Practical Engineering)
## Distributed Global Energy Analytics & Performance Explorer

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-9.0.4-green.svg)](https://www.mongodb.com/)
[![Hadoop](https://img.shields.io/badge/Apache%20Hadoop-3.3.6-orange.svg)](https://hadoop.apache.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-black.svg)](https://flask.palletsprojects.com/)

An end-to-end Big Data Engineering implementation analyzing the **Our World in Data (OWID) Global Energy Dataset** (2000–2024, 6,324 records across 255 countries).

---

## 📌 Project Architecture

- **Theme 1: MongoDB Big Data Analytics**
  - Compound B-Tree Indexing on `{"country": 1, "year": 1}` (`country_year_idx`).
  - **99.984% reduction in document examinations** (1 document examined vs. 6,324 in collection scan).
  - Multi-stage aggregation pipelines: Decadal transition trends, `$unwind` normalization, and `$facet` global summaries.

- **Theme 2: Hadoop HDFS & Streaming MapReduce**
  - Distributed file lifecycle: `-mkdir`, `-put`, `-cat`, `-get` (6,325 lines retrieved with 0 loss), and `-rm -r`.
  - Python Streaming MapReduce deriving 25-year averages, peak annual generation, and clean energy share for 255 countries.
  - Strict `NA` missing-value policy to prevent skewing arithmetic means.

- **Theme 3: Apache Pig & Hive RCFile Benchmarking**
  - Pig Latin data transformation filtering 6,325 records into **5,921 clean rows** (explaining the 403 unobserved totals filtered).
  - Storage Footprint: Standard TextFile (**291,407 bytes**) vs. RCFile Columnar (**64,714 bytes**) — **4.502x storage ratio (77.79% space savings)**.
  - Analytical HQL Queries: Up to **2.54x query speedup** via column projection pruning.

- **Part 2 Extension: Web Dashboard (Flask + Chart.js)**
  - Full-stack web dashboard with 5 REST API endpoints connected natively via PyMongo.
  - Dual-axis interactive time series and top renewable leaders leaderboard.
  - Automated test suite (`test_app.py`) with **100% pass rate (5/5 tests passed)**.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- MongoDB Community Server running on `localhost:27017`
- Python 3.10+ with `flask`, `pymongo`

### 2. Run the Web Dashboard
```bash
cd extension/flask_dashboard
python app.py
```
Open your browser at **`http://127.0.0.1:5000`**.

### 3. Run Automated API Tests
```bash
cd extension/flask_dashboard
python test_app.py
```

---

## 📂 Repository Structure

```
├── data/
│   ├── raw/                      # Raw OWID historical dataset
│   └── processed/                # Validated 2000-2024 analysis subset (6,324 rows)
├── scripts/
│   ├── theme1_mongodb_analytics.py
│   ├── mapreduce/                # mapper.py and reducer.py
│   ├── pig/                      # clean_energy.pig
│   └── hive/                     # setup_tables.hql and benchmark_queries.hql
├── extension/
│   └── flask_dashboard/          # Flask app, test suite, and Chart.js templates
├── notebooks/                    # Turnkey Google Colab notebook
├── results/                      # Real empirical execution logs and output tables
└── docs/                         # Official assignment reports (.docx and .pdf)
```

---

## 👥 Authors
* **Course:** Big Data Analytics (BCS714D) — 2022 Scheme
* **Department:** Computer Science & Engineering, JSSATEB
* **Faculty:** Prof. Sandhiya B
