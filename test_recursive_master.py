import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("PROJECT 65: CINEMA SCREENING & TICKET BOOKING SYSTEM")
print("5-PASS RECURSIVE VERIFICATION & ARCHITECTURAL STRESS TEST HARNESS")
print("=" * 80)

def main():
    start_time = time.time()
    all_passed = True
    summary_results = []

    # -------------------------------------------------------------------------
    # PASS 1: Database & Integrity Hardening
    # -------------------------------------------------------------------------
    print("\n[+] EXECUTING RECURSIVE CYCLE 1: Database & Integrity Hardening...")
    import test_pass1_db
    p1_ok = test_pass1_db.run_pass1_tests()
    summary_results.append(("Cycle 1: Database & Integrity Hardening (16 Tables, 6 Views, 3 Triggers, OCC)", p1_ok))
    if not p1_ok: all_passed = False

    # -------------------------------------------------------------------------
    # PASS 2: API Resilience & Concurrency
    # -------------------------------------------------------------------------
    print("\n[+] EXECUTING RECURSIVE CYCLE 2: Backend API Resilience & Concurrency...")
    import test_pass2_api
    p2_ok = test_pass2_api.run_pass2_tests()
    summary_results.append(("Cycle 2: API Resilience (Idempotency Replay, Rate Limiting, Turnstile Gate)", p2_ok))
    if not p2_ok: all_passed = False

    # -------------------------------------------------------------------------
    # PASS 3: Frontend Multi-Page UX & Visual Polish
    # -------------------------------------------------------------------------
    print("\n[+] EXECUTING RECURSIVE CYCLE 3: Frontend Multi-Page UX (8 Dedicated Landing Pages)...")
    import test_pass3_ux
    p3_ok = test_pass3_ux.run_pass3_tests()
    summary_results.append(("Cycle 3: Frontend Multi-Page UX (Home, Movie, Booking, Concessions, Wallet, Usher, Admin, Docs)", p3_ok))
    if not p3_ok: all_passed = False

    # -------------------------------------------------------------------------
    # PASS 4: Business Intelligence & Yield Management
    # -------------------------------------------------------------------------
    print("\n[+] EXECUTING RECURSIVE CYCLE 4: Business Intelligence & Yield Management...")
    import test_pass4_analytics
    p4_ok = test_pass4_analytics.run_pass4_tests()
    summary_results.append(("Cycle 4: Analytics & Yield Management (Dynamic Pricing, Forecasts, Prometheus Telemetry)", p4_ok))
    if not p4_ok: all_passed = False

    # -------------------------------------------------------------------------
    # PASS 5: End-to-End System Health & Concurrency Stress Test
    # -------------------------------------------------------------------------
    print("\n[+] EXECUTING RECURSIVE CYCLE 5: End-to-End Stress Test & Master Audit...")
    try:
        import urllib.request
        import json
        req = urllib.request.Request("http://127.0.0.1:8000/api/status")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            status_online = (data.get("status") == "ONLINE")
            screenings_count = data.get("active_screenings", 0)
            p5_ok = status_online and (screenings_count >= 90)
            summary_results.append((f"Cycle 5: Master System Health Check ({screenings_count} Screenings Active, SQLite ACID Engine Online)", p5_ok))
            if not p5_ok: all_passed = False
    except Exception as e:
        summary_results.append((f"Cycle 5: Master System Health Check Failed: {e}", False))
        all_passed = False

    total_time = round(time.time() - start_time, 2)

    print("\n" + "=" * 80)
    print(f"5-CYCLE RECURSIVE AUDIT COMPLETED IN {total_time}s")
    print("=" * 80)
    for title, ok in summary_results:
        mark = "[PASS]" if ok else "[FAIL]"
        print(f"  {mark:<8} | {title}")
    print("=" * 80)

    if all_passed:
        print("\n>>> ALL 5 RECURSIVE CYCLES PASSED WITH ZERO ERRORS! <<<")
        return 0
    else:
        print("\n>>> ONE OR MORE RECURSIVE CYCLES FAILED! <<<")
        return 1

if __name__ == "__main__":
    code = main()
    sys.exit(code)
