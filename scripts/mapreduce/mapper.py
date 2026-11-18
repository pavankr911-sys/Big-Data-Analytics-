#!/usr/bin/env python3
"""
Theme 2: Hadoop MapReduce Analytics - Mapper
=============================================
Parses OWID energy records from standard input (CSV format).
Emits key-value pairs:
    Key: country
    Value: year,total_energy_twh,renewables_energy_twh,solar_electricity_twh,wind_electricity_twh

Proper Missing Value Handling:
Preserves missing/empty values as 'NA' rather than silently coercing them to 0.0.
"""

import sys
import csv

def main():
    reader = csv.reader(sys.stdin)
    header = None
    col_idx = {}

    for row in reader:
        if not row:
            continue
        
        # Read header row dynamically
        if header is None:
            header = [col.strip() for col in row]
            col_idx = {name: i for i, name in enumerate(header)}
            required_cols = ["country", "year", "total_energy_twh", "renewables_energy_twh"]
            for col in required_cols:
                if col not in col_idx:
                    sys.stderr.write(f"Error: Missing column '{col}' in header\n")
                    return
            continue

        try:
            country = row[col_idx["country"]].strip()
            year_str = row[col_idx["year"]].strip()
            
            # Skip invalid keys
            if not country or not year_str:
                continue
            
            year = int(year_str)
            if not (2000 <= year <= 2024):
                continue

            # Parse numeric indicators: preserve missing as 'NA'
            def parse_val(col_name):
                idx = col_idx.get(col_name)
                if idx is not None and idx < len(row):
                    val = row[idx].strip()
                    if val != "":
                        try:
                            f = float(val)
                            return f"{f:.3f}"
                        except ValueError:
                            return "NA"
                return "NA"

            total_energy = parse_val("total_energy_twh")
            renewables = parse_val("renewables_energy_twh")
            solar = parse_val("solar_electricity_twh")
            wind = parse_val("wind_electricity_twh")

            # Emit: country \t year,total,renewables,solar,wind
            print(f"{country}\t{year},{total_energy},{renewables},{solar},{wind}")

        except Exception:
            # Skip corrupt rows gracefully
            continue

if __name__ == "__main__":
    main()
