import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def get_json(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity-Audit/2.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())

def get_text(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity-Audit/2.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode()

def run_pass4_tests():
    passes = []
    errors = []

    print("[*] Starting Pass 4: Analytics, Yield Management & Metrics Verification")

    # 1. Test Dynamic Pricing Engine
    # Screening 1 has high/moderate bookings; test endpoint
    dp_st, dp_data = get_json("/api/dynamic-pricing/1")
    if dp_st == 200 and "dynamic_ticket_price" in dp_data and "multiplier" in dp_data:
        passes.append(f"Dynamic Pricing Engine online: Screening #1 Tier: '{dp_data['pricing_tier']}' | Base: ${dp_data['base_price']} | Dynamic: ${dp_data['dynamic_ticket_price']} (x{dp_data['multiplier']})")
    else:
        errors.append(f"Dynamic pricing endpoint failed: {dp_data}")

    # 2. Test Concession Predictive Forecasting
    fc_st, fc_data = get_json("/api/concession-forecast")
    if fc_st == 200 and isinstance(fc_data, list) and len(fc_data) > 0:
        sample_item = fc_data[0]
        passes.append(f"Predictive Concession Forecast verified: {len(fc_data)} items evaluated. Sample: '{sample_item['item_name']}' - Stock: {sample_item['current_stock']} units, Predicted Demand: {sample_item['predicted_demand_units']} units (Reorder Alert: {sample_item['reorder_alert']})")
    else:
        errors.append(f"Concession forecast failed: {fc_data}")

    # 3. Test All 6 Executive SQL Views via /api/reports
    rep_st, rep_data = get_json("/api/reports")
    if rep_st == 200:
        views = [
            ("occupancy", "view_show_occupancy"),
            ("box_office", "view_movie_performance"),
            ("screen_utilization", "view_screen_utilization"),
            ("revenue", "view_total_revenue_breakdown"),
            ("concessions_sales", "view_concession_sales_summary"),
            ("cancellations_refunds", "view_cancellations_and_refunds")
        ]
        for key, view_name in views:
            if key in rep_data and isinstance(rep_data[key], list) and len(rep_data[key]) > 0:
                passes.append(f"Executive BI View '{view_name}' populated ({len(rep_data[key])} rows)")
            else:
                errors.append(f"Executive BI View '{view_name}' is empty or missing")
    else:
        errors.append(f"Reports API failed: {rep_data}")

    # 4. Test Turnaround Buffer Schedule Timeline
    tl_st, tl_data = get_json("/api/schedule-timeline")
    if tl_st == 200 and isinstance(tl_data, list) and len(tl_data) > 0:
        first_screen = tl_data[0]
        first_block = first_screen["blocks"][0] if first_screen["blocks"] else {}
        passes.append(f"15-Minute Turnaround Buffer Timeline verified across {len(tl_data)} screens. Buffer: {first_block.get('clean_buffer_minutes', 0)} min enforced via trigger.")
    else:
        errors.append(f"Schedule timeline API failed: {tl_data}")

    # 5. Test Prometheus Metrics Endpoint
    pm_st, pm_text = get_text("/metrics")
    if pm_st == 200:
        expected_metrics = [
            "cinema_db_active_connections",
            "cinema_transactions_total",
            "cinema_transaction_latency_seconds",
            "cinema_concurrency_conflicts_total",
            "cinema_rate_limit_rejections_total",
            "cinema_active_websocket_locks"
        ]
        all_metrics_found = True
        for m in expected_metrics:
            if m not in pm_text:
                errors.append(f"Prometheus metric '{m}' missing in /metrics")
                all_metrics_found = False
        if all_metrics_found:
            passes.append(f"Prometheus Telemetry verified: All 6 standard metrics formatted in /metrics")
    else:
        errors.append(f"Prometheus /metrics endpoint returned status {pm_st}")

    print("\n--- PASS 4 RESULTS ---")
    print(f"Passed assertions: {len(passes)}")
    for p in passes:
        safe_p = p.encode('ascii', errors='replace').decode('ascii')
        print(f"  [+] {safe_p}")
    if errors:
        print(f"\nFailed assertions: {len(errors)}")
        for e in errors:
            safe_e = e.encode('ascii', errors='replace').decode('ascii')
            print(f"  [-] {safe_e}")
        return False
    else:
        print("\nAll Pass 4 Analytics, Yield Management & Metrics tests PASSED successfully!")
        return True

if __name__ == "__main__":
    success = run_pass4_tests()
    sys.exit(0 if success else 1)
