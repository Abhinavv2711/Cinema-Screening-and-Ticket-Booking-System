import sqlite3

conn = sqlite3.connect('/tmp/cinema_booking.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

test_results = []

# Test 1: Double-booking prevention
try:
    cursor.execute("INSERT INTO booked_seats (booking_id, screening_id, seat_id, price, status) VALUES (2, 1, 1, 450.00, 'Booked');")
    test_results.append(("Double-Booking Prevention", "FAIL - Insert Succeeded unexpectedly"))
except sqlite3.IntegrityError as e:
    test_results.append(("Double-Booking Prevention", f"PASS - Enforced: {e}"))

# Test 2: Screen Overlap Prevention
try:
    cursor.execute("INSERT INTO screenings (screen_id, movie_id, show_date, start_time, end_time, ticket_price, status) VALUES (1, 2, '2026-10-04', '11:00', '13:00', 400.00, 'Scheduled');")
    test_results.append(("Screen Overlap Prevention", "FAIL - Insert Succeeded unexpectedly"))
except sqlite3.IntegrityError as e:
    test_results.append(("Screen Overlap Prevention", f"PASS - Enforced: {e}"))

# Test 3: Positive Quantity on Concession Items
try:
    cursor.execute("INSERT INTO order_items (order_id, item_id, quantity, unit_price, subtotal) VALUES (1, 1, 0, 350.00, 0.00);")
    test_results.append(("Positive Quantity Constraint", "FAIL - Insert Succeeded unexpectedly"))
except sqlite3.IntegrityError as e:
    test_results.append(("Positive Quantity Constraint", f"PASS - Enforced: {e}"))

# Test 4: Refund Limit Exceeded
try:
    cursor.execute("INSERT INTO cancellations (booking_id, reason, cancellation_fee, refund_status) VALUES (2, 'Testing', 0, 'Pending');")
    canc_id = cursor.lastrowid
    cursor.execute("INSERT INTO refunds (cancellation_id, payment_id, refund_amount, refund_reference, status) VALUES (?, 2, 9999.00, 'REF-TEST-OVERLIMIT', 'Processed');", (canc_id,))
    test_results.append(("Refund Limit Constraint", "FAIL - Insert Succeeded unexpectedly"))
except sqlite3.IntegrityError as e:
    test_results.append(("Refund Limit Constraint", f"PASS - Enforced: {e}"))

conn.rollback()
for t_name, res in test_results:
    print(f"[{t_name}]: {res}")

conn.close()
