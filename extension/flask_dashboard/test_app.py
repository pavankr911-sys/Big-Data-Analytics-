"""
Automated Verification Script for Flask Web Dashboard
Tests all REST endpoints and template rendering against local MongoDB.
"""

from app import app
import json

def test_flask_endpoints():
    print("=" * 60)
    print("VERIFYING FLASK DASHBOARD & REST APIS")
    print("=" * 60)

    client = app.test_client()

    # 1. Test index HTML rendering
    print("\n[1] Testing GET / (Dashboard UI)...")
    res_index = client.get("/")
    assert res_index.status_code == 200, f"Expected 200, got {res_index.status_code}"
    assert b"BCS714D Big Data Analytics" in res_index.data
    print("    -> OK: Status 200, Template rendered successfully.")

    # 2. Test /api/kpis
    print("\n[2] Testing GET /api/kpis...")
    res_kpis = client.get("/api/kpis")
    assert res_kpis.status_code == 200
    kpis = res_kpis.get_json()
    print("    -> OK: Status 200, Response:", json.dumps(kpis, indent=2))
    assert kpis["status"] == "success"
    assert kpis["total_documents"] == 6324

    # 3. Test /api/countries
    print("\n[3] Testing GET /api/countries...")
    res_countries = client.get("/api/countries")
    assert res_countries.status_code == 200
    countries = res_countries.get_json()
    print(f"    -> OK: Status 200, Retrieved {len(countries['countries'])} unique countries.")
    assert "India" in countries["countries"]

    # 4. Test /api/country/India
    print("\n[4] Testing GET /api/country/India...")
    res_india = client.get("/api/country/India")
    assert res_india.status_code == 200
    india_data = res_india.get_json()
    records = india_data["data"]
    print(f"    -> OK: Status 200, Retrieved {len(records)} annual records for India (2000–2024).")
    sample_2023 = next((r for r in records if r["year"] == 2023), None)
    print("    -> Sample 2023 India record:", sample_2023)
    assert sample_2023 is not None
    assert sample_2023["total_energy_twh"] > 0

    # 5. Test /api/top_renewables
    print("\n[5] Testing GET /api/top_renewables?year=2023...")
    res_top = client.get("/api/top_renewables?year=2023")
    assert res_top.status_code == 200
    top = res_top.get_json()
    print(f"    -> OK: Status 200, Retrieved {len(top['results'])} renewable leaders.")
    for idx, r in enumerate(top["results"][:5]):
        print(f"       {idx+1}. {r['country']} - {r['renewables_energy_twh']} TWh (Carbon: {r['electricity_carbon_intensity_gco2eq_per_kwh']})")

    print("\n" + "=" * 60)
    print("ALL FLASK DASHBOARD ENDPOINTS TESTED & VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_flask_endpoints()

