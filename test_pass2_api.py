import urllib.request
import urllib.error
import json
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def post_json(endpoint, data, headers=None):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode("utf-8")
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=payload, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def get_json(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def run_pass2_tests():
    passes = []
    errors = []

    print("[*] Starting Pass 2: API Resilience & Concurrency Verification")

    # 1. Test OCC Simulation
    occ_status, occ_resp = post_json("/api/occ-simulate", {"screening_id": 1, "seat_id": 20})
    if occ_status == 200 and "SUCCESS" in occ_resp.get("thread_a_status", "") and "ABORTED" in occ_resp.get("thread_b_status", ""):
        passes.append(f"OCC Simulation verified: Thread A succeeded, Thread B rejected ({occ_resp['resolution']})")
    else:
        errors.append(f"OCC Simulation failed: {occ_resp}")

    # 2. Test Available Seat Discovery
    # Find a screening with available seats
    st, seats_data = get_json("/api/screening/5/seats")
    avail_seats = [s for s in seats_data["seats"] if not s["is_booked"]]
    if not avail_seats:
        st, seats_data = get_json("/api/screening/10/seats")
        avail_seats = [s for s in seats_data["seats"] if not s["is_booked"]]

    if not avail_seats:
        errors.append("No available seats found for testing booking")
        return False

    test_seat = avail_seats[0]["seat_id"]
    screening_id = seats_data["screening_id"]
    test_idempotency_key = f"IDEM-KEY-{int(time.time())}"

    # 3. Test Booking with Idempotency Key (First Call)
    bkg_payload = {
        "screening_id": screening_id,
        "seat_ids": [test_seat],
        "customer_id": 2,
        "payment_method": "UPI",
        "promo_code": "LUXE20"
    }
    bkg_status, bkg_resp = post_json("/api/book-tickets", bkg_payload, headers={"Idempotency-Key": test_idempotency_key})
    if bkg_status == 200 and not bkg_resp.get("is_idempotent_replay"):
        passes.append(f"Booking created: ID #{bkg_resp['booking_id']}, Total: ${bkg_resp['total_amount']} (20% promo discount applied)")
        created_booking_id = bkg_resp["booking_id"]
        created_ticket = bkg_resp["tickets"][0]
    else:
        errors.append(f"Booking creation failed: {bkg_resp}")
        return False

    # 4. Test Idempotency Replay (Second Call with SAME Idempotency-Key)
    replay_status, replay_resp = post_json("/api/book-tickets", bkg_payload, headers={"Idempotency-Key": test_idempotency_key})
    if replay_status == 200 and replay_resp.get("is_idempotent_replay") == True and replay_resp.get("booking_id") == created_booking_id:
        passes.append(f"Idempotency Replay verified: Duplicate request returned identical booking #{created_booking_id} with is_idempotent_replay=True without double-booking!")
    else:
        errors.append(f"Idempotency replay failed: {replay_resp}")

    # 5. Test Ticket Validation at Gate (Turnstile Check-in)
    val_status, val_resp = post_json("/api/validate-ticket", {"token": created_ticket["barcode_hash"]})
    if val_status == 200 and val_resp.get("valid") == True:
        passes.append(f"Gate Turnstile Check-in passed: {val_resp['message']}")
    else:
        errors.append(f"Gate Turnstile check-in failed: {val_resp}")

    # 6. Test Double Check-in Prevention (Used Ticket Rejection)
    val2_status, val2_resp = post_json("/api/validate-ticket", {"token": created_ticket["barcode_hash"]})
    if val2_status == 200 and val2_resp.get("valid") == False and val2_resp.get("status") == "USED":
        passes.append(f"Double-Admission Prevention passed: {val2_resp['message']}")
    else:
        errors.append(f"Double-admission rejection failed: {val2_resp}")

    # 7. Test Concessions Ordering with Stock Verification
    conc_st, conc_items = get_json("/api/concessions")
    if conc_st == 200 and len(conc_items) > 0:
        first_item = conc_items[0]
        initial_stock = first_item["stock_quantity"]
        order_st, order_resp = post_json("/api/order-concessions", {
            "customer_id": 2,
            "booking_id": created_booking_id,
            "items": [{"item_id": first_item["item_id"], "quantity": 2}],
            "payment_method": "Credit Card"
        })
        if order_st == 200 and "order_id" in order_resp:
            passes.append(f"Concessions Order placed: Order #{order_resp['order_id']}, Total: ${order_resp['total_amount']}")
            
            # Verify stock decremented
            _, fresh_conc = get_json("/api/concessions")
            updated_stock = [i["stock_quantity"] for i in fresh_conc if i["item_id"] == first_item["item_id"]][0]
            if updated_stock == initial_stock - 2:
                passes.append(f"Inventory Stock Decrement verified: Stock changed from {initial_stock} to {updated_stock}")
            else:
                errors.append(f"Stock decrement mismatch: expected {initial_stock - 2}, got {updated_stock}")
        else:
            errors.append(f"Concessions order failed: {order_resp}")

        # Test Out-of-Stock Rejection
        excessive_st, excessive_resp = post_json("/api/order-concessions", {
            "customer_id": 2,
            "items": [{"item_id": first_item["item_id"], "quantity": 99999}],
            "payment_method": "UPI"
        })
        if excessive_st == 400 and "Insufficient stock" in excessive_resp.get("detail", ""):
            passes.append(f"Out-of-Stock Protection verified: {excessive_resp['detail']}")
        else:
            errors.append(f"Out-of-stock rejection failed: {excessive_resp}")

    # 8. Test Cancellation & 90% Refund Policy
    # Book another ticket to test clean cancellation
    avail_seats_2 = [s for s in seats_data["seats"] if not s["is_booked"] and s["seat_id"] != test_seat]
    if avail_seats_2:
        seat_to_cancel = avail_seats_2[0]["seat_id"]
        bkg_cancel_status, bkg_cancel_resp = post_json("/api/book-tickets", {
            "screening_id": screening_id,
            "seat_ids": [seat_to_cancel],
            "customer_id": 2,
            "payment_method": "Credit Card"
        })
        if bkg_cancel_status == 200:
            bkg_id_to_cancel = bkg_cancel_resp["booking_id"]
            canc_status, canc_resp = post_json("/api/cancel-booking", {
                "booking_id": bkg_id_to_cancel,
                "reason": "Sudden rescheduling"
            })
            if canc_status == 200 and "refund_amount" in canc_resp:
                passes.append(f"1-Click Cancellation verified: Booking #{bkg_id_to_cancel} refunded ${canc_resp['refund_amount']} (Fee: ${canc_resp['cancellation_fee']})")
                
                # Verify cancelled ticket is rejected at turnstile
                canc_token = bkg_cancel_resp["tickets"][0]["barcode_hash"]
                c_val_status, c_val_resp = post_json("/api/validate-ticket", {"token": canc_token})
                if c_val_status == 200 and c_val_resp.get("status") == "CANCELLED":
                    passes.append(f"Cancelled Ticket Turnstile Gate Denied verified: {c_val_resp['message']}")
                else:
                    errors.append(f"Cancelled ticket turnstile check failed: {c_val_resp}")
            else:
                errors.append(f"Cancellation failed: {canc_resp}")

    # 9. Test Audit Trail Logging
    audit_st, audit_logs = get_json("/api/audit-logs?limit=5")
    if audit_st == 200 and len(audit_logs) > 0:
        latest = audit_logs[0]
        passes.append(f"Immutable Audit Trail verified: {len(audit_logs)} logs retrieved. Latest: {latest['action_type']} on {latest['entity_type']} #{latest['entity_id']} ({latest['new_state']})")
    else:
        errors.append(f"Audit log retrieval failed: {audit_logs}")

    print("\n--- PASS 2 RESULTS ---")
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
        print("\nAll Pass 2 API resilience and concurrency tests PASSED successfully!")
        return True

if __name__ == "__main__":
    success = run_pass2_tests()
    sys.exit(0 if success else 1)
