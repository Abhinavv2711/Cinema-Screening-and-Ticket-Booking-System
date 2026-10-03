#!/usr/bin/env python3
"""
CINEMA SCREENING AND TICKET BOOKING SYSTEM
Small Database Application in Python with SQLite
Woxsen University - School of Technology - DBMS Project-Based Learning (PBL)

Features:
1. Master Show Scheduling with Screen Overlap Trigger Validation (15-min buffer)
2. Visual 2D Seating Matrix with Real-time Booked [X] / Available [O] status
3. ACID Transactional Multi-Seat Booking with Unique SHA-256 Digital Barcodes
4. Real-time Concession Ordering with Stock Quantity Validation and Auto-Depletion
5. Payment Transaction Processing (UPI, Credit/Debit Card, Net Banking, Cash)
6. Booking Cancellation & Automated Refund Limits Validation (10% Fee Policy)
7. Executive Management Reports (Occupancy, Box Office, Screen Utilization, Concessions, Net Revenue)
8. Interactive CLI Menu and Automated System Diagnostics Verification
"""

import sqlite3
import hashlib
import sys
import os
import datetime

# ----------------------------------------------------------------------
# DATABASE PATH DISCOVERY
# ----------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
POSSIBLE_PATHS = [
    os.path.join(APP_DIR, "cinema_booking.db"),
    os.path.join(APP_DIR, "..", "sql", "cinema_booking.db"),
    os.path.join(os.getcwd(), "cinema_booking.db"),
    os.path.join(os.getcwd(), "project", "sql", "cinema_booking.db"),
    os.path.join(os.getcwd(), "project", "app", "cinema_booking.db")
]

DB_PATH = None
for p in POSSIBLE_PATHS:
    if os.path.exists(p) and os.path.getsize(p) > 0:
        DB_PATH = os.path.abspath(p)
        break

if not DB_PATH:
    # If no database found, default to local directory
    DB_PATH = os.path.abspath(os.path.join(APP_DIR, "cinema_booking.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def header(title):
    print("\n" + "=" * 70)
    print(f"  {title.upper()}")
    print("=" * 70)

# ----------------------------------------------------------------------
# MODULE 1: SHOW SCHEDULING (CREATE / READ)
# ----------------------------------------------------------------------
def list_screenings():
    header("Scheduled Movie Screenings")
    conn = get_connection()
    cur = conn.cursor()
    query = """
    SELECT 
        s.screening_id,
        c.name AS cinema_name,
        sc.screen_number,
        sc.screen_type,
        m.title AS movie_title,
        s.show_date,
        s.start_time,
        s.end_time,
        s.ticket_price,
        s.status
    FROM screenings s
    JOIN screens sc ON s.screen_id = sc.screen_id
    JOIN cinemas c ON sc.cinema_id = c.cinema_id
    JOIN movies m ON s.movie_id = m.movie_id
    WHERE s.status != 'Cancelled'
    ORDER BY s.show_date, s.start_time;
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    print(f"{'ID':<4} | {'Cinema':<22} | {'Scrn':<4} | {'Type':<8} | {'Movie':<16} | {'Date':<10} | {'Time':<11} | {'Price':<7}")
    print("-" * 98)
    for r in rows:
        time_slot = f"{r[6]}-{r[7]}"
        print(f"{r[0]:<4} | {r[1][:22]:<22} | {r[2]:<4} | {r[3]:<8} | {r[4][:16]:<16} | {r[5]:<10} | {time_slot:<11} | Rs.{int(r[8]):<5}")
    return rows

def schedule_screening(screen_id, movie_id, show_date, start_time, end_time, ticket_price):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO screenings (screen_id, movie_id, show_date, start_time, end_time, ticket_price, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Scheduled')
        """, (screen_id, movie_id, show_date, start_time, end_time, ticket_price))
        conn.commit()
        screening_id = cur.lastrowid
        return True, f"Screening successfully scheduled! Screening ID: #{screening_id}"
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return False, f"Schedule Collision Error: {e}"
    finally:
        conn.close()

# ----------------------------------------------------------------------
# MODULE 2: VISUAL 2D SEAT MATRIX & AVAILABILITY
# ----------------------------------------------------------------------
def display_seat_matrix(screening_id):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT m.title, c.name, sc.screen_number, sc.screen_type, s.show_date, s.start_time, sc.screen_id
        FROM screenings s
        JOIN screens sc ON s.screen_id = sc.screen_id
        JOIN cinemas c ON sc.cinema_id = c.cinema_id
        JOIN movies m ON s.movie_id = m.movie_id
        WHERE s.screening_id = ?
    """, (screening_id,))
    show_info = cur.fetchone()
    if not show_info:
        conn.close()
        print("Screening ID not found.")
        return
        
    title, cinema, screen_num, screen_type, s_date, s_time, screen_id = show_info
    header(f"SEAT MATRIX: {title} ({screen_type}) @ {cinema} (SCREEN {screen_num})")
    print(f"Date: {s_date} | Time: {s_time} | [O] = Available | [X] = Booked\n")
    print("                ================ AUDITORIUM SCREEN ================\n")
    
    cur.execute("""
        SELECT seat_id, row_label, seat_number, seat_tier, base_price
        FROM seats
        WHERE screen_id = ?
        ORDER BY row_label, seat_number;
    """, (screen_id,))
    all_seats = cur.fetchall()
    
    cur.execute("""
        SELECT seat_id FROM booked_seats
        WHERE screening_id = ? AND status = 'Booked';
    """, (screening_id,))
    booked_ids = set(r[0] for r in cur.fetchall())
    conn.close()
    
    rows_dict = {}
    for sid, row_lbl, s_num, tier, price in all_seats:
        if row_lbl not in rows_dict:
            rows_dict[row_lbl] = {"tier": tier, "price": price, "seats": []}
        status_char = "[X]" if sid in booked_ids else f"[{s_num:02d}]"
        rows_dict[row_lbl]["seats"].append((sid, status_char))
        
    for r_lbl in sorted(rows_dict.keys()):
        tier = rows_dict[r_lbl]["tier"]
        price = int(rows_dict[r_lbl]["price"])
        seat_display = " ".join(s[1] for s in rows_dict[r_lbl]["seats"])
        print(f"  Row {r_lbl} ({tier:<8} Rs.{price}):   {seat_display}")
    print("\n" + "-" * 70)

# ----------------------------------------------------------------------
# MODULE 3: ATOMIC MULTI-SEAT TICKET BOOKING & ISSUANCE
# ----------------------------------------------------------------------
def book_tickets(customer_id, screening_id, seat_ids, payment_method="UPI"):
    if not seat_ids:
        return False, "Error: No seats selected for booking."
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION;")
        
        cur.execute("SELECT ticket_price FROM screenings WHERE screening_id = ?", (screening_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Screening does not exist.")
        unit_price = row[0]
        
        placeholders = ','.join(['?'] * len(seat_ids))
        cur.execute(f"""
            SELECT seat_id FROM booked_seats
            WHERE screening_id = ? AND seat_id IN ({placeholders}) AND status = 'Booked'
        """, [screening_id] + seat_ids)
        already_booked = cur.fetchall()
        if already_booked:
            conflicted = [str(r[0]) for r in already_booked]
            raise ValueError(f"Seat(s) {', '.join(conflicted)} already booked! Double booking prevented.")
        
        total_amount = unit_price * len(seat_ids)
        
        cur.execute("""
            INSERT INTO bookings (customer_id, screening_id, total_amount, booking_status)
            VALUES (?, ?, ?, 'Confirmed')
        """, (customer_id, screening_id, total_amount))
        booking_id = cur.lastrowid
        
        tickets_issued = []
        for sid in seat_ids:
            cur.execute("""
                INSERT INTO booked_seats (booking_id, screening_id, seat_id, price, status)
                VALUES (?, ?, ?, ?, 'Booked')
            """, (booking_id, screening_id, sid, unit_price))
            booked_seat_id = cur.lastrowid
            
            ticket_number = f"TKT-BKG{booking_id}-S{sid}-{datetime.datetime.now().strftime('%y%m%d')}"
            raw_hash_data = f"{ticket_number}-{screening_id}-{sid}-{datetime.datetime.now().isoformat()}"
            barcode_hash = hashlib.sha256(raw_hash_data.encode()).hexdigest()[:16]
            
            cur.execute("""
                INSERT INTO tickets (booking_id, booked_seat_id, ticket_number, barcode_hash, status)
                VALUES (?, ?, ?, ?, 'Active')
            """, (booking_id, booked_seat_id, ticket_number, barcode_hash))
            tickets_issued.append((ticket_number, barcode_hash, sid))
            
        txn_ref = f"TXN-{payment_method[:3].upper()}-{booking_id}-{datetime.datetime.now().strftime('%H%M%S')}"
        cur.execute("""
            INSERT INTO payments (booking_id, order_id, amount, payment_method, transaction_reference, payment_status)
            VALUES (?, NULL, ?, ?, ?, 'Success')
        """, (booking_id, total_amount, payment_method, txn_ref))
        
        conn.commit()
        return True, {
            "booking_id": booking_id,
            "total_amount": total_amount,
            "transaction_reference": txn_ref,
            "tickets": tickets_issued
        }
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# ----------------------------------------------------------------------
# MODULE 4: CONCESSIONS ORDERING & INVENTORY MANAGEMENT
# ----------------------------------------------------------------------
def list_concession_items():
    header("Cinema Concession Menu & Live Stock")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT item_id, item_name, category, unit_price, stock_quantity FROM concession_items ORDER BY category, item_name;")
    rows = cur.fetchall()
    conn.close()
    
    print(f"{'ID':<4} | {'Item Name':<34} | {'Category':<10} | {'Price':<8} | {'Stock':<6}")
    print("-" * 72)
    for r in rows:
        print(f"{r[0]:<4} | {r[1]:<34} | {r[2]:<10} | Rs.{int(r[3]):<5} | {r[4]:<6}")
    return rows

def order_concessions(customer_id, booking_id, item_qty_pairs, payment_method="UPI"):
    conn = get_connection()
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION;")
        total_order_amount = 0.0
        validated_items = []
        
        for item_id, qty in item_qty_pairs:
            if qty <= 0:
                raise ValueError(f"Quantity must be strictly positive (> 0). Provided: {qty}")
            cur.execute("SELECT item_name, unit_price, stock_quantity FROM concession_items WHERE item_id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Concession item ID {item_id} does not exist.")
            name, price, stock = row
            if stock < qty:
                raise ValueError(f"Insufficient stock for '{name}'. Requested: {qty}, Available: {stock}.")
            subtotal = price * qty
            total_order_amount += subtotal
            validated_items.append((item_id, qty, price, subtotal))
            
        cur.execute("""
            INSERT INTO orders (booking_id, customer_id, total_amount, order_status)
            VALUES (?, ?, ?, 'Placed')
        """, (booking_id, customer_id, total_order_amount))
        order_id = cur.lastrowid
        
        for item_id, qty, price, subtotal in validated_items:
            cur.execute("""
                INSERT INTO order_items (order_id, item_id, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, item_id, qty, price, subtotal))
            cur.execute("""
                UPDATE concession_items
                SET stock_quantity = stock_quantity - ?
                WHERE item_id = ?
            """, (qty, item_id))
            
        txn_ref = f"TXN-CONC-{order_id}-{datetime.datetime.now().strftime('%H%M%S')}"
        cur.execute("""
            INSERT INTO payments (booking_id, order_id, amount, payment_method, transaction_reference, payment_status)
            VALUES (NULL, ?, ?, ?, ?, 'Success')
        """, (order_id, total_order_amount, payment_method, txn_ref))
        
        conn.commit()
        return True, {"order_id": order_id, "total_amount": total_order_amount, "txn_ref": txn_ref}
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# ----------------------------------------------------------------------
# MODULE 5: BOOKING CANCELLATION & REFUNDS
# ----------------------------------------------------------------------
def cancel_booking(booking_id, reason="Customer Change of Plans"):
    conn = get_connection()
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION;")
        cur.execute("""
            SELECT b.booking_status, b.total_amount, p.payment_id, p.amount
            FROM bookings b
            JOIN payments p ON b.booking_id = p.booking_id
            WHERE b.booking_id = ? AND p.payment_status = 'Success';
        """, (booking_id,))
        res = cur.fetchone()
        if not res:
            raise ValueError(f"Booking #{booking_id} not found or payment not finalized.")
        status, total_amt, payment_id, paid_amount = res
        if status == 'Cancelled':
            raise ValueError(f"Booking #{booking_id} is already cancelled.")
            
        cancellation_fee = round(paid_amount * 0.10, 2)
        refund_amount = round(paid_amount - cancellation_fee, 2)
        
        cur.execute("UPDATE bookings SET booking_status = 'Cancelled' WHERE booking_id = ?;", (booking_id,))
        cur.execute("UPDATE booked_seats SET status = 'Cancelled' WHERE booking_id = ?;", (booking_id,))
        cur.execute("UPDATE tickets SET status = 'Cancelled' WHERE booking_id = ?;", (booking_id,))
        
        cur.execute("""
            INSERT INTO cancellations (booking_id, reason, cancellation_fee, refund_status)
            VALUES (?, ?, ?, 'Approved');
        """, (booking_id, reason, cancellation_fee))
        canc_id = cur.lastrowid
        
        refund_ref = f"REF-{booking_id}-{datetime.datetime.now().strftime('%H%M%S')}"
        cur.execute("""
            INSERT INTO refunds (cancellation_id, payment_id, refund_amount, refund_reference, status)
            VALUES (?, ?, ?, ?, 'Processed');
        """, (canc_id, payment_id, refund_amount, refund_ref))
        
        conn.commit()
        return True, {
            "booking_id": booking_id,
            "cancellation_fee": cancellation_fee,
            "refund_amount": refund_amount,
            "refund_reference": refund_ref
        }
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# ----------------------------------------------------------------------
# MODULE 6: EXECUTIVE REPORTS & ANALYTICS VIEWS
# ----------------------------------------------------------------------
def generate_reports():
    conn = get_connection()
    cur = conn.cursor()
    
    header("REPORT 1: SHOW OCCUPANCY ANALYSIS")
    cur.execute("SELECT screening_id, movie_title, cinema_name, screen_number, show_date, start_time, booked_seats, total_seats, occupancy_percentage FROM view_show_occupancy ORDER BY occupancy_percentage DESC;")
    for r in cur.fetchall():
        print(f"Show #{r[0]:<2} | {r[1]:<16} @ {r[2][:16]} (Scrn {r[3]}) | {r[4]} {r[5]} | Booked: {r[6]}/{r[7]} ({r[8]}%)")
        
    header("REPORT 2: MOVIE BOX OFFICE PERFORMANCE")
    cur.execute("SELECT movie_title, genre, total_screenings, tickets_sold, box_office_gross FROM view_movie_performance ORDER BY box_office_gross DESC;")
    for r in cur.fetchall():
        print(f"Movie: {r[0]:<16} | Genre: {r[1]:<16} | Shows: {r[2]} | Tickets: {r[3]:<3} | Gross: Rs.{r[4]:<10.2f}")
        
    header("REPORT 3: SCREEN UTILIZATION & RUNTIME EFFICIENCY")
    cur.execute("SELECT cinema_name, screen_number, screen_type, total_shows_scheduled, operational_hours_runtime, average_capacity_utilization FROM view_screen_utilization;")
    for r in cur.fetchall():
        print(f"{r[0][:20]:<20} | Screen {r[1]} ({r[2]}) | Shows: {r[3]} | Runtime: {r[4]:.1f} hrs | Cap. Util: {r[5]}%")

    header("REPORT 4: CONCESSION SALES & INVENTORY")
    cur.execute("SELECT item_name, category, total_units_sold, current_stock, total_revenue FROM view_concession_sales_summary ORDER BY total_revenue DESC;")
    for r in cur.fetchall():
        print(f"{r[0]:<32} | Cat: {r[1]:<8} | Sold: {r[2]:<3} | Stock: {r[3]:<4} | Rev: Rs.{r[4]:<8.2f}")

    header("REPORT 5: TOTAL FINANCIAL & NET REVENUE SUMMARY")
    cur.execute("SELECT cinema_name, ticket_revenue, concession_revenue, cancellation_penalties_retained, total_refunds_disbursed, net_operating_revenue FROM view_total_revenue_breakdown;")
    for r in cur.fetchall():
        print(f"Cinema: {r[0]}")
        print(f"  + Ticket Box Office Revenue    : Rs. {r[1]:>8.2f}")
        print(f"  + Concession Sales Revenue     : Rs. {r[2]:>8.2f}")
        print(f"  + Cancellation Fees Retained   : Rs. {r[3]:>8.2f}")
        print(f"  - Customer Refunds Disbursed   : Rs. {r[4]:>8.2f}")
        print(f"  = NET OPERATING REVENUE        : Rs. {r[5]:>8.2f}\n")
    conn.close()

# ----------------------------------------------------------------------
# MODULE 7: SYSTEM DIAGNOSTICS & CONSTRAINT VERIFICATION
# ----------------------------------------------------------------------
def run_diagnostics():
    header("SYSTEM DIAGNOSTICS & CONSTRAINT VERIFICATION")
    conn = get_connection()
    cur = conn.cursor()
    tests = []
    
    try:
        cur.execute("INSERT INTO booked_seats (booking_id, screening_id, seat_id, price, status) VALUES (1, 1, 1, 350, 'Booked');")
        tests.append(("Double-Booking Prevention", "FAIL", "Allowed duplicate active seat on same screening"))
    except sqlite3.IntegrityError as e:
        tests.append(("Double-Booking Prevention", "PASS", f"Enforced via unique index ({e})"))
        
    try:
        cur.execute("INSERT INTO screenings (screen_id, movie_id, show_date, start_time, end_time, ticket_price, status) VALUES (1, 1, '2026-10-04', '11:00:00', '13:00:00', 300, 'Scheduled');")
        tests.append(("Screen Overlap Trigger", "FAIL", "Allowed overlapping showtime on Screen 1"))
    except sqlite3.IntegrityError as e:
        tests.append(("Screen Overlap Trigger", "PASS", f"Enforced via trigger ({e})"))
        
    try:
        cur.execute("INSERT INTO order_items (order_id, item_id, quantity, unit_price, subtotal) VALUES (1, 1, -5, 350, -1750);")
        tests.append(("Positive Quantity Check", "FAIL", "Allowed negative purchase quantity"))
    except sqlite3.IntegrityError as e:
        tests.append(("Positive Quantity Check", "PASS", f"Enforced via CHECK ({e})"))
        
    try:
        cur.execute("INSERT INTO refunds (cancellation_id, payment_id, refund_amount, refund_reference, status) VALUES (999, 1, 99999.00, 'REF-TEST-OVERFLOW', 'Processed');")
        tests.append(("Refund Limit Enforcement", "FAIL", "Allowed refund exceeding original payment"))
    except sqlite3.IntegrityError as e:
        tests.append(("Refund Limit Enforcement", "PASS", f"Enforced via refund limit trigger ({e})"))
        
    conn.rollback()
    conn.close()
    
    for t_name, status, details in tests:
        print(f"[{status}] {t_name:<28} : {details}")

def run_automated_demo():
    print("\n" + "=" * 70)
    print("  RUNNING AUTOMATED END-TO-END DEMONSTRATION")
    print("=" * 70)
    list_screenings()
    display_seat_matrix(1)
    
    # Dynamically find 2 available seats for screening 1
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.seat_id FROM seats s
        WHERE s.screen_id = (SELECT screen_id FROM screenings WHERE screening_id = 1)
          AND s.seat_id NOT IN (
              SELECT seat_id FROM booked_seats WHERE screening_id = 1 AND status = 'Booked'
          )
        ORDER BY s.seat_id
        LIMIT 2;
    """)
    avail = [r[0] for r in cur.fetchall()]
    conn.close()
    test_seats = avail if len(avail) >= 2 else [15, 16]

    print(f"\n>> Executing New Ticket Booking Transaction (Customer 2, Screening 1, Seats {test_seats})...")
    ok, res = book_tickets(customer_id=2, screening_id=1, seat_ids=test_seats, payment_method="Credit Card")
    booking_id = None
    if ok and isinstance(res, dict):
        booking_id = res.get("booking_id")
        print(f"Booking Confirmed! ID: #{booking_id} | Total: Rs.{res['total_amount']} | Txn: {res['transaction_reference']}")
        for t in res.get("tickets", []):
            print(f"  -> Ticket #{t[0]} issued for Seat ID {t[2]} [Digital Hash: {t[1]}]")
    else:
        print("Booking Notice:", res)
        
    print("\n>> Executing Concession Purchase (Customer 2, 1x Nachos, 2x Coca Cola)...")
    c_ok, c_res = order_concessions(customer_id=2, booking_id=booking_id, item_qty_pairs=[(5, 1), (3, 2)], payment_method="Credit Card")
    if c_ok and isinstance(c_res, dict):
        print(f"Concession Order Processed! Order ID: #{c_res['order_id']} | Total: Rs.{c_res['total_amount']} | Ref: {c_res['txn_ref']}")
    else:
        print("Concession Order Failed:", c_res)
        
    print("\n>> Generating Management Analytics:")
    generate_reports()
    
    print("\n>> Running System Diagnostics & Negative Tests:")
    run_diagnostics()

# ----------------------------------------------------------------------
# INTERACTIVE TERMINAL MENU LOOP
# ----------------------------------------------------------------------
def interactive_menu():
    while True:
        print("\n" + "=" * 70)
        print("  CINEMA SCREENING AND TICKET BOOKING SYSTEM - MAIN MENU")
        print("=" * 70)
        print("1. Browse Scheduled Movie Screenings")
        print("2. View Seating Matrix & Availability")
        print("3. Book Movie Tickets (Interactive Seat Selection)")
        print("4. Concessions & Food Ordering")
        print("5. Cancel a Booking & Process Refund")
        print("6. View Executive Analytics & Management Reports")
        print("7. Run Automated Diagnostics & Constraint Integrity Tests")
        print("8. Run Full Automated System Demonstration")
        print("9. Exit Application")
        print("-" * 70)
        choice = input("Enter your choice (1-9): ").strip()
        
        if choice == "1":
            list_screenings()
        elif choice == "2":
            sid = input("Enter Screening ID (default 1): ").strip() or "1"
            try:
                display_seat_matrix(int(sid))
            except ValueError:
                print("Invalid Screening ID.")
        elif choice == "3":
            list_screenings()
            sid_str = input("\nEnter Screening ID to book: ").strip() or "1"
            display_seat_matrix(int(sid_str))
            seats_str = input("Enter Seat IDs separated by commas (e.g. 6, 7): ").strip()
            if not seats_str:
                print("No seats provided.")
                continue
            try:
                seat_ids = [int(s.strip()) for s in seats_str.split(",") if s.strip()]
                cust_id = int(input("Enter Customer ID (default 2): ").strip() or "2")
                pmethod = input("Enter Payment Method (UPI / Credit Card / Cash) [default UPI]: ").strip() or "UPI"
                ok, res = book_tickets(cust_id, int(sid_str), seat_ids, pmethod)
                if ok and isinstance(res, dict):
                    print(f"\n[SUCCESS] Booking Confirmed! ID: #{res['booking_id']} | Total: Rs.{res['total_amount']} | Txn: {res['transaction_reference']}")
                    for t in res.get("tickets", []):
                        print(f"  -> Ticket #{t[0]} issued for Seat ID {t[2]} [Digital Hash: {t[1]}]")
                else:
                    print(f"\n[FAILED] Booking Error: {res}")
            except Exception as e:
                print("Error during booking:", e)
        elif choice == "4":
            list_concession_items()
            items_str = input("\nEnter Item ID and Quantity pairs (e.g. '1:2, 3:1' for 2x Item 1 and 1x Item 3): ").strip()
            if items_str:
                try:
                    pairs = []
                    for part in items_str.split(","):
                        it, qt = part.strip().split(":")
                        pairs.append((int(it), int(qt)))
                    cust_id = int(input("Enter Customer ID (default 2): ").strip() or "2")
                    ok, res = order_concessions(cust_id, None, pairs, "UPI")
                    if ok and isinstance(res, dict):
                        print(f"\n[SUCCESS] Order #{res['order_id']} placed! Total: Rs.{res['total_amount']} | Txn: {res['txn_ref']}")
                    else:
                        print(f"\n[FAILED] Order Error: {res}")
                except Exception as e:
                    print("Invalid input format:", e)
        elif choice == "5":
            b_id = input("Enter Booking ID to cancel: ").strip()
            if b_id:
                reason = input("Enter cancellation reason: ").strip() or "Customer Cancellation"
                ok, res = cancel_booking(int(b_id), reason)
                if ok and isinstance(res, dict):
                    print(f"\n[SUCCESS] Booking #{res['booking_id']} cancelled!")
                    print(f"  Fee Retained (10%): Rs.{res['cancellation_fee']}")
                    print(f"  Refund Issued: Rs.{res['refund_amount']} (Ref: {res['refund_reference']})")
                else:
                    print(f"\n[FAILED] Cancellation Error: {res}")
        elif choice == "6":
            generate_reports()
        elif choice == "7":
            run_diagnostics()
        elif choice == "8":
            run_automated_demo()
        elif choice == "9":
            print("\nThank you for using Cinema Screening & Ticket Booking System. Exiting...")
            break
        else:
            print("Invalid choice. Please select an option between 1 and 9.")
            
        input("\nPress Enter to return to main menu...")

# ----------------------------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_automated_demo()
    elif not sys.stdin.isatty():
        run_automated_demo()
    else:
        try:
            interactive_menu()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting application...")
