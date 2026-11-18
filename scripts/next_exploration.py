
import pandas as pd

df = pd.read_csv("data/raw/owid_energy.csv")

# 1. Year range
print("\n--- YEAR COVERAGE ---")
print("Earliest year:", df["year"].min())
print("Latest year:", df["year"].max())
print("Unique years:", df["year"].nunique())

# 2. Country/location coverage
print("\n--- LOCATION COVERAGE ---")
print("Unique locations:", df["country"].nunique())
print("Top 10 locations by record count:")
print(df["country"].value_counts().head(10))

# 3. Duplicate country-year combinations
print("\n--- COUNTRY-YEAR DUPLICATES ---")
duplicate_keys = df.duplicated(
    subset=["country", "year"], keep=False
)
print("Rows belonging to duplicate country-year pairs:",
      duplicate_keys.sum())

if duplicate_keys.any():
    print(df.loc[duplicate_keys, ["country", "year"]]
          .sort_values(["country", "year"]).head(20))

# 4. Missing-value percentages
print("\n--- MISSING-VALUE PERCENTAGES ---")
missing_pct = df.isnull().mean().mul(100)
print(missing_pct.sort_values(ascending=False).head(15).round(2))

# 5. Most complete indicators
print("\n--- MOST COMPLETE COLUMNS ---")
print(missing_pct.sort_values().head(15).round(2))

# 6. Inspect India
print("\n--- INDIA SAMPLE ---")
india = df[df["country"].str.lower() == "india"]
print(india[[
    "country", "year", "population",
    "total_energy_twh",
    "renewables_energy_twh",
    "electricity_generation_twh"
]].tail(10).to_string(index=False))
