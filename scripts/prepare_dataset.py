
import pandas as pd
from pathlib import Path

# Project paths
source = Path("data/raw/owid_energy.csv")
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

# Load original dataset
df = pd.read_csv(source)

print("Original shape:", df.shape)

# Validate essential columns
required = ["country", "year", "iso_code"]
missing_columns = [c for c in required if c not in df.columns]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Validate country and year keys
df["country"] = df["country"].astype("string").str.strip()
df["year"] = pd.to_numeric(df["year"], errors="coerce")

invalid_keys = df["country"].isna() | df["year"].isna()

print("Rows with invalid country/year:", invalid_keys.sum())

# Keep valid keys and convert year to integer
df = df.loc[~invalid_keys].copy()
df["year"] = df["year"].astype("int64")

# Check country-year duplicates; do not silently delete them
duplicates = df.duplicated(
    subset=["country", "year"], keep=False
)

print("Rows with duplicate country-year keys:", duplicates.sum())

if duplicates.any():
    print(df.loc[duplicates, ["country", "year"]].head(20))
    raise ValueError("Resolve duplicate keys before continuing.")

# Create a consistent analysis-period dataset
analysis = df[df["year"].between(2000, 2024)].copy()

# Save the full validated dataset and analysis-period dataset
df.to_csv(output_dir / "energy_validated.csv", index=False)
analysis.to_csv(output_dir / "energy_2000_2024.csv", index=False)

print("\n--- PREPARATION SUMMARY ---")
print("Validated dataset:", df.shape)
print("Analysis-period dataset:", analysis.shape)
print("Year range:", analysis["year"].min(), "-", analysis["year"].max())
print("Unique locations:", analysis["country"].nunique())

print("\nFiles saved:")
print(output_dir / "energy_validated.csv")
print(output_dir / "energy_2000_2024.csv")
