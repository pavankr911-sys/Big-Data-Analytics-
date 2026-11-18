
import pandas as pd

# Load the original energy dataset
file_path = "data/raw/owid_energy.csv"
df = pd.read_csv(file_path)

# 1. Dataset size
print("\n--- DATASET SIZE ---")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# 2. Preview the records
print("\n--- FIRST 5 ROWS ---")
print(df.head().to_string())

# 3. Inspect column names
print("\n--- COLUMN NAMES ---")
for column in df.columns:
    print(column)

# 4. Check data types
print("\n--- DATA TYPES ---")
print(df.dtypes.to_string())

# 5. Missing values
print("\n--- TOP 15 MISSING-VALUE COUNTS ---")
print(df.isnull().sum().sort_values(ascending=False).head(15))

# 6. Duplicate rows
print("\n--- DUPLICATES ---")
print("Duplicate rows:", df.duplicated().sum())

# 7. Check likely key columns
print("\n--- KEY COLUMNS ---")
print("Location column:", 
      next((c for c in ["country", "entity", "location"]
            if c in df.columns), "Not found"))

print("Year column present:", "year" in df.columns)
