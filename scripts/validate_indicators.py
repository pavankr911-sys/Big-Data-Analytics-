
import pandas as pd

df = pd.read_csv("data/raw/owid_energy.csv")

indicators = [
    "total_energy_twh",
    "renewables_energy_twh",
    "solar_electricity_twh",
    "wind_electricity_twh",
    "electricity_carbon_intensity_gco2eq_per_kwh",
]

print("\n--- INDICATOR VALIDATION ---")

for col in indicators:
    available = df[col].notna().sum()
    missing = df[col].isna().sum()

    print(f"\n{col}")
    print("Available values:", available)
    print("Missing values:", missing)
    print("Completeness (%):", round(100 * available / len(df), 2))

print("\n--- YEAR COVERAGE FOR INDIA ---")

india = df[df["country"] == "India"]

for col in indicators:
    valid = india.loc[india[col].notna(), ["year", col]]

    if not valid.empty:
        print(
            f"{col}: {valid['year'].min()}–{valid['year'].max()}, "
            f"{len(valid)} available records"
        )

print("\n--- COUNTRY COMPARISON: 2024 ---")

year_data = df[df["year"] == 2024]

for col in ["total_energy_twh",
            "electricity_carbon_intensity_gco2eq_per_kwh"]:
    valid = year_data[["country", col]].dropna()

    print(f"\n{col}: {len(valid)} records")
    print(valid.sort_values(col, ascending=False).head(10).to_string(index=False))
