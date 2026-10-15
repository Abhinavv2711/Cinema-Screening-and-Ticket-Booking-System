import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSSIBLE_PATHS = [
    os.path.join(BASE_DIR, "cinema_booking_system_git_package", "project", "app", "cinema_booking.db"),
    os.path.join(BASE_DIR, "cinema_booking_system_git_package", "project", "sql", "cinema_booking.db"),
    os.path.join(BASE_DIR, "cinema_booking.db"),
    os.path.join(BASE_DIR, "project", "app", "cinema_booking.db"),
]

DB_PATH = None
for p in POSSIBLE_PATHS:
    if os.path.exists(p) and os.path.getsize(p) > 0:
        DB_PATH = os.path.abspath(p)
        break

if not DB_PATH:
    DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "cinema_booking.db"))

print(f"[*] Testing Database at: {DB_PATH}")

def run_pass1_tests():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    errors = []
    passes = []

    # 1. Verify 16 Relational Tables
    expected_tables = [
        "cinemas", "screens", "seats", "movies", "screenings", "customers",
        "bookings", "booked_seats", "tickets", "cancellations", "payments",
        "refunds", "concession_items", "orders", "order_items", "audit_log"
    ]
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = set(r[0] for r in cur.fetchall())

    for t in expected_tables:
        if t in existing_tables:
            cur.execute(f"SELECT COUNT(*) FROM {t};")
            cnt = cur.fetchone()[0]
            passes.append(f"Table '{t}' exists ({cnt} records)")
        else:
            errors.append(f"Missing table '{t}'")

    # 2. Verify 6 Analytical Views
    expected_views = [
        "view_show_occupancy", "view_movie_performance", "view_screen_utilization",
        "view_total_revenue_breakdown", "view_concession_sales_summary", "view_cancellations_and_refunds"
    ]
    cur.execute("SELECT name FROM sqlite_master WHERE type='view';")
    existing_views = set(r[0] for r in cur.fetchall())

    for v in expected_views:
        if v in existing_views:
            cur.execute(f"SELECT COUNT(*) FROM {v};")
            cnt = cur.fetchone()[0]
            passes.append(f"View '{v}' valid ({cnt} rows returned)")
        else:
            errors.append(f"Missing view '{v}'")

    # 3. Verify Triggers & Indexes
    cur.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
    existing_triggers = set(r[0] for r in cur.fetchall())
    expected_triggers = [
        "trg_prevent_screen_overlap_insert",
        "trg_prevent_screen_overlap_update",
        "trg_check_refund_limit"
    ]
    for trg in expected_triggers:
        if trg in existing_triggers:
            passes.append(f"Trigger '{trg}' present")
        else:
            errors.append(f"Missing trigger '{trg}'")

    # 4. Test Trigger: Screen Overlap Prevention
    try:
        # Screen 1 already has a show at 2026-10-04 10:00:00 - 13:00:00
        cur.execute("""
            INSERT INTO screenings (screen_id, movie_id, show_date, start_time, end_time, ticket_price, status)
            VALUES (1, 1, '2026-10-04', '11:00:00', '13:30:00', 350.0, 'Scheduled');
        """)
        conn.commit()
        errors.append("FAILED: Overlapping screening was allowed on Screen 1!")
    except sqlite3.IntegrityError as e:
        passes.append(f"Trigger Overlap Prevention passed: {e}")
        conn.rollback()

    # 5. Test Unique Constraint: Duplicate Active Seat Booking
    try:
        # Screen 1, screening 1, seat 1 is already booked
        cur.execute("""
            INSERT INTO booked_seats (booking_id, screening_id, seat_id, price, status)
            VALUES (1, 1, 1, 350.0, 'Booked');
        """)
        conn.commit()
        errors.append("FAILED: Duplicate seat booking was allowed!")
    except sqlite3.IntegrityError as e:
        passes.append(f"Double-Booking Prevention passed: {e}")
        conn.rollback()

    # 6. Test CHECK Constraint: Negative Item Quantity
    try:
        cur.execute("""
            INSERT INTO order_items (order_id, item_id, quantity, unit_price, subtotal)
            VALUES (1, 1, -10, 250.0, -2500.0);
        """)
        conn.commit()
        errors.append("FAILED: Negative order item quantity was allowed!")
    except sqlite3.IntegrityError as e:
        passes.append(f"Negative Quantity CHECK constraint passed: {e}")
        conn.rollback()

    # 7. Test Trigger: Excessive Refund Amount
    try:
        cur.execute("""
            INSERT INTO refunds (cancellation_id, payment_id, refund_amount, refund_reference, status)
            VALUES (999, 1, 999999.00, 'REF-OVERFLOW-TEST', 'Processed');
        """)
        conn.commit()
        errors.append("FAILED: Excessive refund exceeding payment was allowed!")
    except sqlite3.IntegrityError as e:
        passes.append(f"Excessive Refund Trigger passed: {e}")
        conn.rollback()

    # 8. Check OCC version_id column
    cur.execute("PRAGMA table_info(seats);")
    seat_cols = [c[1] for c in cur.fetchall()]
    if "version_id" in seat_cols:
        passes.append("Seat version_id column present for OCC")
    else:
        errors.append("Missing version_id column on seats table")

    # 9. Check Multi-date Screenings distribution
    cur.execute("SELECT show_date, COUNT(*) FROM screenings GROUP BY show_date ORDER BY show_date;")
    date_counts = cur.fetchall()
    passes.append(f"Multi-Date Screenings: {len(date_counts)} distinct dates available: {date_counts}")

    conn.close()

    print("\n--- PASS 1 RESULTS ---")
    print(f"Passed assertions: {len(passes)}")
    for p in passes:
        print(f"  [+] {p}")
    if errors:
        print(f"\nFailed assertions: {len(errors)}")
        for e in errors:
            print(f"  [-] {e}")
        return False
    else:
        print("\nAll Pass 1 DB integrity tests PASSED successfully!")
        return True

if __name__ == "__main__":
    success = run_pass1_tests()
    sys.exit(0 if success else 1)
