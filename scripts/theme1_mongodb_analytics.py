"""
Theme 1: MongoDB Big Data Processing & Analytics
================================================
Implements:
1. Ingestion & Index Verification (collection: energy_data_clean, index: country_year_idx)
2. Advanced Aggregation Pipelines using $match, $group, $project, $unwind, and $facet
3. Query Performance Profiling with .explain("executionStats") (IXSCAN vs COLLSCAN)
"""

import json
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient

def run_mongodb_analytics():
    print("=" * 60)
    print("BCS714D TRACK B - THEME 1: MONGODB ANALYTICS & PROFILING")
    print("=" * 60)

    client = MongoClient("mongodb://localhost:27017/")
    db = client["energy_analytics"]
    coll = db["energy_data_clean"]

    # 1. Verification
    total_docs = coll.count_documents({})
    indexes = list(coll.list_indexes())
    index_names = [idx["name"] for idx in indexes]
    print(f"\n[1] Collection Verification:")
    print(f"    - Target Collection: energy_data_clean")
    print(f"    - Total Documents: {total_docs}")
    print(f"    - Existing Indexes: {index_names}")
    assert total_docs == 6324, f"Expected 6,324 documents, found {total_docs}"
    assert "country_year_idx" in index_names, "Missing compound index 'country_year_idx'"

    # 2. Aggregation Pipelines: $match, $project, $group, $unwind, $facet
    print(f"\n[2] Executing Aggregation Pipelines ($match, $group, $project, $unwind, $facet)...")

    # Pipeline A: Multi-stage Aggregation ($match, $project, $group)
    # Computes 5-year decadal energy transition trends for selected major emerging & developed economies
    pipeline_trends = [
        {
            "$match": {
                "country": {"$in": ["India", "China", "United States", "Germany", "Brazil"]},
                "year": {"$gte": 2000, "$lte": 2024},
                "total_energy_twh": {"$gt": 0}
            }
        },
        {
            "$project": {
                "country": 1,
                "year": 1,
                "total_energy_twh": 1,
                "renewables_energy_twh": 1,
                "solar_electricity_twh": 1,
                "wind_electricity_twh": 1,
                "electricity_carbon_intensity_gco2eq_per_kwh": 1,
                "period": {
                    "$concat": [
                        {"$toString": {"$subtract": ["$year", {"$mod": [{"$subtract": ["$year", 2000]}, 5]}]}},
                        "-",
                        {"$toString": {"$add": [{"$subtract": ["$year", {"$mod": [{"$subtract": ["$year", 2000]}, 5]}]}, 4]}}
                    ]
                },
                "renewable_pct": {
                    "$cond": [
                        {"$gt": ["$total_energy_twh", 0]},
                        {"$multiply": [{"$divide": ["$renewables_energy_twh", "$total_energy_twh"]}, 100]},
                        0
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "country": "$country",
                    "period": "$period"
                },
                "avg_total_energy_twh": {"$avg": "$total_energy_twh"},
                "avg_renewables_energy_twh": {"$avg": "$renewables_energy_twh"},
                "avg_solar_twh": {"$avg": "$solar_electricity_twh"},
                "avg_wind_twh": {"$avg": "$wind_electricity_twh"},
                "avg_carbon_intensity": {"$avg": "$electricity_carbon_intensity_gco2eq_per_kwh"},
                "avg_renewable_pct": {"$avg": "$renewable_pct"},
                "record_count": {"$sum": 1}
            }
        },
        {
            "$sort": {
                "_id.country": 1,
                "_id.period": 1
            }
        }
    ]

    trends_results = list(coll.aggregate(pipeline_trends))
    print(f"    -> Decadal trend aggregation generated {len(trends_results)} group periods.")

    # Pipeline B: $unwind transformation
    # Restructures multi-indicator measurements into normalized indicator entries
    pipeline_unwind = [
        {
            "$match": {
                "country": "India",
                "year": {"$in": [2000, 2010, 2020, 2023]}
            }
        },
        {
            "$project": {
                "_id": 0,
                "country": 1,
                "year": 1,
                "indicators": [
                    {"type": "total_energy", "value": "$total_energy_twh", "unit": "TWh"},
                    {"type": "renewables_energy", "value": "$renewables_energy_twh", "unit": "TWh"},
                    {"type": "solar_electricity", "value": "$solar_electricity_twh", "unit": "TWh"},
                    {"type": "wind_electricity", "value": "$wind_electricity_twh", "unit": "TWh"},
                    {"type": "carbon_intensity", "value": "$electricity_carbon_intensity_gco2eq_per_kwh", "unit": "gCO2/kWh"}
                ]
            }
        },
        {
            "$unwind": "$indicators"
        },
        {
            "$project": {
                "country": 1,
                "year": 1,
                "indicator": "$indicators.type",
                "value": "$indicators.value",
                "unit": "$indicators.unit"
            }
        },
        {
            "$sort": {"year": 1, "indicator": 1}
        }
    ]

    unwind_results = list(coll.aggregate(pipeline_unwind))
    print(f"    -> Unwind aggregation generated {len(unwind_results)} individual indicator records.")

    # Pipeline C: $facet for multi-dimensional analytical dashboard
    # Runs 3 sub-pipelines concurrently:
    # 1. Top 5 Renewable Producers (2023)
    # 2. Lowest Carbon Intensity Clean Leaders (2023, min 50 TWh total energy)
    # 3. Global Statistical Summary (2023)
    pipeline_facet = [
        {
            "$match": {
                "year": 2023,
                "iso_code": {"$exists": True, "$ne": None, "$nin": ["OWID_WRL", ""]}
            }
        },
        {
            "$facet": {
                "top_renewable_producers": [
                    {"$match": {"renewables_energy_twh": {"$gt": 0}}},
                    {"$sort": {"renewables_energy_twh": -1}},
                    {"$limit": 5},
                    {
                        "$project": {
                            "_id": 0,
                            "country": 1,
                            "iso_code": 1,
                            "renewables_energy_twh": 1,
                            "total_energy_twh": 1
                        }
                    }
                ],
                "cleanest_power_grids": [
                    {
                        "$match": {
                            "total_energy_twh": {"$gt": 50},
                            "electricity_carbon_intensity_gco2eq_per_kwh": {"$gt": 0}
                        }
                    },
                    {"$sort": {"electricity_carbon_intensity_gco2eq_per_kwh": 1}},
                    {"$limit": 5},
                    {
                        "$project": {
                            "_id": 0,
                            "country": 1,
                            "iso_code": 1,
                            "electricity_carbon_intensity_gco2eq_per_kwh": 1,
                            "total_energy_twh": 1
                        }
                    }
                ],
                "global_summary_2023": [
                    {
                        "$group": {
                            "_id": None,
                            "total_countries": {"$sum": 1},
                            "sum_total_energy_twh": {"$sum": "$total_energy_twh"},
                            "sum_renewables_energy_twh": {"$sum": "$renewables_energy_twh"},
                            "avg_carbon_intensity": {"$avg": "$electricity_carbon_intensity_gco2eq_per_kwh"}
                        }
                    },
                    {"$project": {"_id": 0}}
                ]
            }
        }
    ]

    facet_results = list(coll.aggregate(pipeline_facet))[0]
    print(f"    -> Facet aggregation computed 3 parallel analytical facets:")
    print(f"       * Top Renewables: {len(facet_results['top_renewable_producers'])} countries")
    print(f"       * Cleanest Grids: {len(facet_results['cleanest_power_grids'])} countries")
    print(f"       * Global Summary: {facet_results['global_summary_2023']}")

    # 3. Query Performance Profiling (.explain("executionStats"))
    print(f"\n[3] Evaluating Query Performance Profiling (.explain('executionStats'))...")

    # A. Indexed Query using compound index country_year_idx
    indexed_explain = coll.find(
        {"country": "India", "year": 2023}
    ).explain()

    # In pymongo, explain() without args returns queryPlanner + executionStats by default or we can request executionStats
    db.command({
        "explain": {
            "find": "energy_data_clean",
            "filter": {"country": "India", "year": 2023}
        },
        "verbosity": "executionStats"
    })
    indexed_stats = db.command({
        "explain": {
            "find": "energy_data_clean",
            "filter": {"country": "India", "year": 2023}
        },
        "verbosity": "executionStats"
    })

    # B. Collection Scan (COLLSCAN) using natural hint
    scan_stats = db.command({
        "explain": {
            "find": "energy_data_clean",
            "filter": {"country": "India", "year": 2023},
            "hint": {"$natural": 1}
        },
        "verbosity": "executionStats"
    })

    # Extract profiling metrics
    def extract_metrics(stats_obj, label):
        exec_stats = stats_obj.get("executionStats", {})
        query_planner = stats_obj.get("queryPlanner", {})
        winning_plan = query_planner.get("winningPlan", {})

        return {
            "query_type": label,
            "stage": winning_plan.get("stage") or winning_plan.get("inputStage", {}).get("stage", "UNKNOWN"),
            "index_name": winning_plan.get("inputStage", {}).get("indexName", "None (COLLSCAN)"),
            "nReturned": exec_stats.get("nReturned"),
            "totalDocsExamined": exec_stats.get("totalDocsExamined"),
            "totalKeysExamined": exec_stats.get("totalKeysExamined", 0),
            "executionTimeMillis": exec_stats.get("executionTimeMillis"),
            "executionSuccess": exec_stats.get("executionSuccess")
        }

    idx_metric = extract_metrics(indexed_stats, "Indexed Query (country_year_idx)")
    scan_metric = extract_metrics(scan_stats, "Collection Scan ($natural COLLSCAN)")

    print(f"    -> Indexed Query Execution Stats:")
    print(f"       * Stage: {idx_metric['stage']}")
    print(f"       * Index: {idx_metric['index_name']}")
    print(f"       * Keys Examined: {idx_metric['totalKeysExamined']}")
    print(f"       * Docs Examined: {idx_metric['totalDocsExamined']}")
    print(f"       * Documents Returned: {idx_metric['nReturned']}")
    print(f"       * Execution Time: {idx_metric['executionTimeMillis']} ms")

    print(f"    -> Collection Scan Execution Stats:")
    print(f"       * Stage: {scan_metric['stage']}")
    print(f"       * Index: {scan_metric['index_name']}")
    print(f"       * Keys Examined: {scan_metric['totalKeysExamined']}")
    print(f"       * Docs Examined: {scan_metric['totalDocsExamined']}")
    print(f"       * Documents Returned: {scan_metric['nReturned']}")
    print(f"       * Execution Time: {scan_metric['executionTimeMillis']} ms")

    # 4. Save Artifacts & Results to results/mongodb/
    out_dir = Path("results/mongodb")
    out_dir.mkdir(parents=True, exist_ok=True)

    aggregation_payload = {
        "timestamp": datetime.now().isoformat(),
        "database": "energy_analytics",
        "collection": "energy_data_clean",
        "total_documents": total_docs,
        "pipelines_executed": [
            "decadal_country_trends ($match, $project, $group)",
            "indicator_unwind ($match, $project, $unwind)",
            "country_facet_dashboard ($match, $facet)"
        ],
        "decadal_country_trends": trends_results,
        "indicator_unwind_sample": unwind_results[:20],
        "facet_dashboard": facet_results
    }

    profiling_payload = {
        "timestamp": datetime.now().isoformat(),
        "database": "energy_analytics",
        "collection": "energy_data_clean",
        "total_documents": total_docs,
        "index_used": "country_year_idx",
        "comparison": [idx_metric, scan_metric],
        "detailed_indexed_stats": indexed_stats["executionStats"],
        "detailed_scan_stats": scan_stats["executionStats"]
    }

    with open(out_dir / "theme1_aggregation_results.json", "w", encoding="utf-8") as f:
        json.dump(aggregation_payload, f, indent=2, default=str)

    with open(out_dir / "theme1_performance_profiling.json", "w", encoding="utf-8") as f:
        json.dump(profiling_payload, f, indent=2, default=str)

    # Also update performance_results collection in MongoDB
    perf_coll = db["performance_results"]
    perf_coll.delete_many({})
    perf_coll.insert_many([
        {
            "experiment": "Indexed Query (country_year_idx)",
            "filter": {"country": "India", "year": 2023},
            "index": "country_year_idx",
            "stage": idx_metric["stage"],
            "totalKeysExamined": idx_metric["totalKeysExamined"],
            "totalDocsExamined": idx_metric["totalDocsExamined"],
            "nReturned": idx_metric["nReturned"],
            "executionTimeMillis": idx_metric["executionTimeMillis"],
            "recorded_at": datetime.now()
        },
        {
            "experiment": "Collection Scan (Forced Natural Order)",
            "filter": {"country": "India", "year": 2023},
            "index": "None (COLLSCAN)",
            "stage": scan_metric["stage"],
            "totalKeysExamined": scan_metric["totalKeysExamined"],
            "totalDocsExamined": scan_metric["totalDocsExamined"],
            "nReturned": scan_metric["nReturned"],
            "executionTimeMillis": scan_metric["executionTimeMillis"],
            "recorded_at": datetime.now()
        }
    ])

    print(f"\n[4] Artifacts Successfully Saved:")
    print(f"    - {out_dir / 'theme1_aggregation_results.json'}")
    print(f"    - {out_dir / 'theme1_performance_profiling.json'}")
    print(f"    - Updated 'performance_results' collection in MongoDB.")
    print("\nTheme 1 successfully verified with genuine execution statistics!")

if __name__ == "__main__":
    run_mongodb_analytics()

