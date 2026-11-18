#!/usr/bin/env python3
"""
Theme 2: Hadoop MapReduce Analytics - Reducer
=============================================
Aggregates mapper output grouped by 'country'.

Proper Missing Value Handling:
- Missing measurements ('NA') are excluded from indicator averages (avoids denominator dilution).
- Separate valid-year counters are maintained for each indicator.
- If an indicator has no valid records, 'NA' is emitted rather than a misleading '0.00'.
"""

import sys

def parse_num(val_str):
    if val_str == "NA" or val_str == "":
        return None
    try:
        return float(val_str)
    except ValueError:
        return None

def emit_record(country, records):
    if not records:
        return

    n_years = len(records)

    # Collect valid measurements per indicator
    valid_totals = [(r["year"], r["total"]) for r in records if r["total"] is not None]
    valid_renews = [(r["year"], r["renewables"]) for r in records if r["renewables"] is not None]
    valid_solars = [(r["year"], r["solar"]) for r in records if r["solar"] is not None]
    valid_winds  = [(r["year"], r["wind"]) for r in records if r["wind"] is not None]

    # Compute indicator averages using only valid observed values
    avg_total_str = f"{sum(v for _, v in valid_totals) / len(valid_totals):.2f}" if valid_totals else "NA"
    avg_renew_str = f"{sum(v for _, v in valid_renews) / len(valid_renews):.2f}" if valid_renews else "NA"
    avg_solar_str = f"{sum(v for _, v in valid_solars) / len(valid_solars):.2f}" if valid_solars else "NA"
    avg_wind_str  = f"{sum(v for _, v in valid_winds) / len(valid_winds):.2f}"   if valid_winds  else "NA"

    # Peak values
    if valid_totals:
        peak_total_yr, peak_total_val = max(valid_totals, key=lambda x: x[1])
        peak_total_str = f"{peak_total_val:.2f} ({peak_total_yr})"
    else:
        peak_total_str = "NA"

    if valid_renews:
        peak_renew_yr, peak_renew_val = max(valid_renews, key=lambda x: x[1])
        peak_renew_str = f"{peak_renew_val:.2f} ({peak_renew_yr})"
    else:
        peak_renew_str = "NA"

    # Renewable penetration percentage
    if valid_totals and valid_renews:
        avg_tot_num = sum(v for _, v in valid_totals) / len(valid_totals)
        avg_ren_num = sum(v for _, v in valid_renews) / len(valid_renews)
        if avg_tot_num > 0:
            avg_renew_pct_str = f"{(avg_ren_num / avg_tot_num * 100.0):.2f}%"
        else:
            avg_renew_pct_str = "0.00%"
    else:
        avg_renew_pct_str = "NA"

    print(
        f"{country}\t"
        f"{n_years}\t"
        f"{avg_total_str}\t"
        f"{avg_renew_str}\t"
        f"{avg_solar_str}\t"
        f"{avg_wind_str}\t"
        f"{peak_total_str}\t"
        f"{peak_renew_str}\t"
        f"{avg_renew_pct_str}"
    )

def main():
    current_country = None
    current_records = []

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue

        country, val_str = parts
        vals = val_str.split(",")
        if len(vals) < 5:
            continue

        try:
            year = int(vals[0])
        except ValueError:
            continue

        record = {
            "year": year,
            "total": parse_num(vals[1]),
            "renewables": parse_num(vals[2]),
            "solar": parse_num(vals[3]),
            "wind": parse_num(vals[4])
        }

        if current_country == country:
            current_records.append(record)
        else:
            if current_country is not None:
                emit_record(current_country, current_records)
            current_country = country
            current_records = [record]

    # Emit final group
    if current_country is not None:
        emit_record(current_country, current_records)

if __name__ == "__main__":
    main()
