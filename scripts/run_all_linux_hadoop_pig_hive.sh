#!/usr/bin/env bash
# ==============================================================================
# BCS714D Big Data Analytics - Track B Practical Automation Script
# Runs Themes 2 & 3: Hadoop HDFS, YARN MapReduce, Pig Latin & Hive RCFile Benchmarking
# ==============================================================================
set -e

PROJECT_DIR=$(pwd)
RESULTS_DIR="$PROJECT_DIR/results"
mkdir -p "$RESULTS_DIR/hdfs" "$RESULTS_DIR/mapreduce" "$RESULTS_DIR/pig" "$RESULTS_DIR/hive"

echo "=============================================================================="
echo "BCS714D BIG DATA ANALYTICS: THEMES 2 & 3 EXECUTION HARNESS"
echo "=============================================================================="

# ------------------------------------------------------------------------------
# STEP 1: Java 8 & Hadoop Environment Validation
# ------------------------------------------------------------------------------
echo -e "\n[STEP 1] Validating Java & Hadoop Environment..."
if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
fi
if [ -z "$HADOOP_HOME" ]; then
    export HADOOP_HOME=${HADOOP_HOME:-/usr/local/hadoop}
fi
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

echo "Hadoop version:"
hadoop version | head -n 2

# Check running daemons
echo "Checking active Hadoop daemons (jps):"
jps

# ------------------------------------------------------------------------------
# STEP 2: Theme 2 - HDFS Operations
# ------------------------------------------------------------------------------
echo -e "\n[STEP 2] Executing Mandatory HDFS Operations..."
HDFS_LOG="$RESULTS_DIR/hdfs/hdfs_operations.log"
exec > >(tee -a "$HDFS_LOG") 2>&1

INPUT_CSV="$PROJECT_DIR/data/processed/energy_2000_2024.csv"
HDFS_INPUT_DIR="/energy_project/input"
HDFS_SCRATCH_DIR="/energy_project/scratch_temp"

echo ">>> 2.1: Creating HDFS directories (hdfs dfs -mkdir)"
hdfs dfs -mkdir -p "$HDFS_INPUT_DIR"
hdfs dfs -mkdir -p "$HDFS_SCRATCH_DIR"
hdfs dfs -ls /energy_project

echo ">>> 2.2: Uploading dataset to HDFS (hdfs dfs -put)"
hdfs dfs -put -f "$INPUT_CSV" "$HDFS_INPUT_DIR/energy_2000_2024.csv"
hdfs dfs -ls -h "$HDFS_INPUT_DIR"

echo ">>> 2.3: Viewing data in HDFS (hdfs dfs -cat)"
echo "--- Head 5 records from HDFS ---"
hdfs dfs -cat "$HDFS_INPUT_DIR/energy_2000_2024.csv" | head -n 5

echo ">>> 2.4: Retrieving data from HDFS (hdfs dfs -get)"
mkdir -p /tmp/hdfs_verify
hdfs dfs -get -f "$HDFS_INPUT_DIR/energy_2000_2024.csv" /tmp/hdfs_verify/retrieved_energy.csv
echo "Retrieved file lines: $(wc -l < /tmp/hdfs_verify/retrieved_energy.csv)"

echo ">>> 2.5: Deleting test directory (hdfs dfs -rm -r)"
hdfs dfs -rm -r "$HDFS_SCRATCH_DIR"
hdfs dfs -ls /energy_project

echo "HDFS operations successfully verified and logged."

# ------------------------------------------------------------------------------
# STEP 3: Theme 2 - MapReduce Execution on YARN
# ------------------------------------------------------------------------------
echo -e "\n[STEP 3] Executing MapReduce Job on YARN..."
MR_LOG="$RESULTS_DIR/mapreduce/mapreduce_yarn.log"
HDFS_MR_OUT="/energy_project/output_mr"

hdfs dfs -rm -r -f "$HDFS_MR_OUT" 2>/dev/null || true

STREAMING_JAR=$(find $HADOOP_HOME/share/hadoop/tools/lib/ -name "hadoop-streaming-*.jar" | head -n 1)
echo "Found Streaming Jar: $STREAMING_JAR"

START_TIME=$(date +%s%N)

hadoop jar "$STREAMING_JAR" \
    -files "$PROJECT_DIR/scripts/mapreduce/mapper.py,$PROJECT_DIR/scripts/mapreduce/reducer.py" \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py" \
    -input "$HDFS_INPUT_DIR/energy_2000_2024.csv" \
    -output "$HDFS_MR_OUT" \
    2>&1 | tee "$MR_LOG"

END_TIME=$(date +%s%N)
MR_DURATION_SEC=$(( (END_TIME - START_TIME) / 1000000000 ))

echo "MapReduce Job finished in: $MR_DURATION_SEC seconds"

# Retrieve MapReduce output
hdfs dfs -get -f "$HDFS_MR_OUT/part-00000" "$RESULTS_DIR/mapreduce/part-00000.tsv"
echo "Top 15 MapReduce Country Transition Summaries:"
head -n 15 "$RESULTS_DIR/mapreduce/part-00000.tsv"

# ------------------------------------------------------------------------------
# STEP 4: Theme 3 - Apache Pig Transformation
# ------------------------------------------------------------------------------
echo -e "\n[STEP 4] Executing Apache Pig Data Transformation..."
PIG_LOG="$RESULTS_DIR/pig/pig_execution.log"
HDFS_PIG_OUT="/energy_project/pig_cleaned"

# Set Pig Classpath for Hadoop 3 compatibility
export PIG_CLASSPATH=$($HADOOP_HOME/bin/hadoop classpath)

hdfs dfs -rm -r -f "$HDFS_PIG_OUT" 2>/dev/null || true

pig -x mapreduce \
    -param INPUT="$HDFS_INPUT_DIR/energy_2000_2024.csv" \
    -param OUTPUT="$HDFS_PIG_OUT" \
    "$PROJECT_DIR/scripts/pig/clean_energy.pig" \
    2>&1 | tee "$PIG_LOG"

echo "Pig Transformation output preview:"
hdfs dfs -cat "$HDFS_PIG_OUT/part-*" | head -n 10
hdfs dfs -get -f "$HDFS_PIG_OUT/part-*" "$RESULTS_DIR/pig/pig_cleaned_sample.csv" 2>/dev/null || true

# ------------------------------------------------------------------------------
# STEP 5: Theme 3 - Hive RCFile vs Text Benchmarking
# ------------------------------------------------------------------------------
echo -e "\n[STEP 5] Setting up Hive Tables & Benchmarking RCFile vs Text..."
HIVE_LOG="$RESULTS_DIR/hive/hive_benchmarking.log"

# Fix Guava conflict if Hive is present
if [ -d "$HIVE_HOME" ]; then
    rm -f $HIVE_HOME/lib/guava-19.0.jar 2>/dev/null || true
    cp $HADOOP_HOME/share/hadoop/common/lib/guava-*.jar $HIVE_HOME/lib/ 2>/dev/null || true
fi

# Setup tables and ingest
hive -hiveconf PIG_OUTPUT_PATH="$HDFS_PIG_OUT" -f "$PROJECT_DIR/scripts/hive/setup_tables.hql" 2>&1 | tee "$HIVE_LOG"

# Measure Genuine Storage Footprint
echo -e "\n[STEP 5.1] Measuring HDFS Disk Footprint..."
hdfs dfs -du -h /user/hive/warehouse/energy_analytics_hive.db/ > "$RESULTS_DIR/hive/hdfs_storage_footprint.txt"
cat "$RESULTS_DIR/hive/hdfs_storage_footprint.txt"

# Run Benchmark Queries
echo -e "\n[STEP 5.2] Executing Benchmark Queries..."
hive -f "$PROJECT_DIR/scripts/hive/benchmark_queries.hql" 2>&1 | tee -a "$HIVE_LOG"

echo "=============================================================================="
echo "ALL THEMES COMPLETED AND ARTIFACTS RECORDED SUCCESSFULLY"
echo "=============================================================================="
