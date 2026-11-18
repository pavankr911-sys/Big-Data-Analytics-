"""
BCS714D Big Data Analytics - Track B Practical Extension
========================================================
Flask Web Dashboard & Visualization Application
Connects to MongoDB 'energy_analytics' database (energy_data_clean collection)
Provides analytical REST APIs and interactive Chart.js web dashboard.
"""

from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# Connect to local MongoDB instance
client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
db = client["energy_analytics"]
collection = db["energy_data_clean"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/kpis")
def get_kpis():
    try:
        total_docs = collection.count_documents({})
        countries = len(collection.distinct("country"))
        
        # 2023 global aggregates
        pipeline_2023 = [
            {"$match": {"year": 2023, "iso_code": {"$exists": True, "$ne": None, "$nin": ["OWID_WRL", ""]}}},
            {
                "$group": {
                    "_id": None,
                    "global_total_energy": {"$sum": "$total_energy_twh"},
                    "global_renewables": {"$sum": "$renewables_energy_twh"},
                    "avg_carbon_intensity": {"$avg": "$electricity_carbon_intensity_gco2eq_per_kwh"}
                }
            }
        ]
        agg_2023 = list(collection.aggregate(pipeline_2023))
        kpi_data = agg_2023[0] if agg_2023 else {}

        tot_energy = kpi_data.get("global_total_energy", 0)
        tot_renewables = kpi_data.get("global_renewables", 0)
        renewable_pct = (tot_renewables / tot_energy * 100) if tot_energy > 0 else 0

        return jsonify({
            "status": "success",
            "total_documents": total_docs,
            "unique_countries": countries,
            "year_range": "2000 - 2024",
            "global_total_energy_2023_twh": round(tot_energy, 2),
            "global_renewables_2023_twh": round(tot_renewables, 2),
            "global_renewable_penetration_pct": round(renewable_pct, 2),
            "avg_carbon_intensity_gco2_kwh": round(kpi_data.get("avg_carbon_intensity", 0), 2)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/countries")
def get_countries():
    try:
        # Get countries that have valid ISO codes or significant data
        countries = collection.distinct("country")
        countries = sorted([c for c in countries if c and not c.startswith("OWID")])
        return jsonify({"status": "success", "countries": countries})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/country/<country_name>")
def get_country_data(country_name):
    try:
        records = list(collection.find(
            {"country": country_name, "year": {"$gte": 2000, "$lte": 2024}},
            {
                "_id": 0,
                "country": 1,
                "year": 1,
                "total_energy_twh": 1,
                "renewables_energy_twh": 1,
                "solar_electricity_twh": 1,
                "wind_electricity_twh": 1,
                "electricity_carbon_intensity_gco2eq_per_kwh": 1
            }
        ).sort("year", 1))

        if not records:
            return jsonify({"status": "not_found", "message": f"No data found for '{country_name}'"}), 404

        # Clean null values to 0 for chart safety
        for r in records:
            for k in ["total_energy_twh", "renewables_energy_twh", "solar_electricity_twh", "wind_electricity_twh", "electricity_carbon_intensity_gco2eq_per_kwh"]:
                r[k] = round(r.get(k) or 0.0, 2)
            r["renewable_pct"] = round((r["renewables_energy_twh"] / r["total_energy_twh"] * 100) if r["total_energy_twh"] > 0 else 0.0, 2)

        return jsonify({
            "status": "success",
            "country": country_name,
            "data": records
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/top_renewables")
def get_top_renewables():
    try:
        year = int(request.args.get("year", 2023))
        pipeline = [
            {
                "$match": {
                    "year": year,
                    "iso_code": {"$exists": True, "$ne": None, "$nin": ["OWID_WRL", ""]},
                    "renewables_energy_twh": {"$gt": 0}
                }
            },
            {"$sort": {"renewables_energy_twh": -1}},
            {"$limit": 10},
            {
                "$project": {
                    "_id": 0,
                    "country": 1,
                    "iso_code": 1,
                    "total_energy_twh": {"$round": ["$total_energy_twh", 2]},
                    "renewables_energy_twh": {"$round": ["$renewables_energy_twh", 2]},
                    "solar_electricity_twh": {"$round": ["$solar_electricity_twh", 2]},
                    "wind_electricity_twh": {"$round": ["$wind_electricity_twh", 2]},
                    "electricity_carbon_intensity_gco2eq_per_kwh": {"$round": ["$electricity_carbon_intensity_gco2eq_per_kwh", 2]}
                }
            }
        ]
        results = list(collection.aggregate(pipeline))
        return jsonify({"status": "success", "year": year, "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("Starting BCS714D Energy Analytics Flask Web Dashboard on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)

