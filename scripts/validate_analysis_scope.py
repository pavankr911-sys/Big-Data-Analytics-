
import pandas as pd

df = pd.read_csv("data/raw/owid_energy.csv")

indicators = [
    "total_energy_twh",
    "renewables_energy_twh",
    "solar_electricity_twh",
    "wind_electricity_twh",
    "electricity_carbon_intensity_gco2eq_per_kwh",
]

# A. Check India from 2000 through 2024
india = df[
    (df["country"] == "India") &
    (df["year"].between(2000, 2024))
]

print("--- INDIA: 2000–2024 ---")
for col in indicators:
    print(f"{col}: {india[col].notna().sum()} / {len(india)} values")

# B. Inspect country codes in the 2024 data
data_2024 = df[df["year"] == 2024]

print("\n--- ISO CODE EXAMPLES ---")
print(data_2024[["country", "iso_code"]].head(30).to_string(index=False))

print("\n--- MISSING ISO CODES ---")
print(data_2024["iso_code"].isna().sum())

# C. Compare all records with coded records
print("\n--- TOTAL ENERGY: 2024 ---")
print("All locations:",
      data_2024["total_energy_twh"].notna().sum())

coded = data_2024[
    data_2024["iso_code"].notna() &
    data_2024["total_energy_twh"].notna()
]
print("Records with ISO codes and total energy:", len(coded))

print("\nTop coded records (inspect before finalizing country rankings):")
print(coded[["country", "iso_code", "total_energy_twh"]]
      .sort_values("total_energy_twh", ascending=False)
      .head(15).to_string(index=False))

# D. Check unique year coverage for the chosen period
print("\n--- AVAILABLE YEARS ---")
print(sorted(india["year"].unique()))
