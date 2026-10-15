import sqlite3
import hashlib
import datetime
import os
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# 1. DATABASE PATH DISCOVERY
# -----------------------------------------------------------------------------
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

def get_connection():
    """Create fresh SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# -----------------------------------------------------------------------------
# 2. FASTAPI SETUP & MIDDLEWARE
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Cinema Screening & Ticket Booking Engine",
    description="High-performance DBMS backend with ACID multi-seat reservation, cryptographic SHA-256 tickets, and live analytics.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# 3. PYDANTIC SCHEMAS
# -----------------------------------------------------------------------------
class SeatModel(BaseModel):
    seat_id: int
    row_label: str
    seat_number: int
    seat_tier: str
    base_price: float
    is_booked: bool

class ScreeningDetails(BaseModel):
    screening_id: int
    movie_title: str
    cinema_name: str
    screen_number: int
    screen_type: str
    show_date: str
    start_time: str
    end_time: str
    ticket_price: float
    total_seats: int
    booked_count: int
    seats: List[SeatModel]

class BookingRequest(BaseModel):
    screening_id: int
    seat_ids: List[int]
    customer_id: int = 2
    payment_method: str = "UPI"
    promo_code: Optional[str] = None

class TicketIssued(BaseModel):
    ticket_number: str
    seat_id: int
    barcode_hash: str

class BookingResponse(BaseModel):
    booking_id: int
    subtotal: float
    discount: float
    total_amount: float
    transaction_reference: str
    tickets: List[TicketIssued]

class ConcessionOrderItem(BaseModel):
    item_id: int
    quantity: int

class ConcessionOrderRequest(BaseModel):
    customer_id: int = 2
    booking_id: Optional[int] = None
    items: List[ConcessionOrderItem]
    payment_method: str = "UPI"

class CancellationRequest(BaseModel):
    booking_id: int
    reason: str = "Customer change of plans"

class ValidationRequest(BaseModel):
    token: str

# -----------------------------------------------------------------------------
# 4. REST API ENDPOINTS
# -----------------------------------------------------------------------------

@app.get("/api/status")
def get_system_status():
    """Returns database connection status and constraint triggers."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM screenings WHERE status != 'Cancelled'")
    active_shows = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bookings WHERE booking_status = 'Confirmed'")
    confirmed_bkgs = cur.fetchone()[0]
    conn.close()
    return {
        "status": "ONLINE",
        "engine": "SQLite3 ACID",
        "db_path": DB_PATH,
        "active_screenings": active_shows,
        "confirmed_bookings": confirmed_bkgs,
        "triggers_enforced": [
            "trg_prevent_screen_overlap_insert",
            "trg_prevent_screen_overlap_update",
            "trg_check_refund_limit",
            "uq_screening_seat_active"
        ]
    }

@app.get("/api/screenings")
def list_screenings():
    """Lists all active movie screenings across all cinema auditoriums."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
    SELECT 
        s.screening_id,
        m.movie_id,
        m.title AS movie_title,
        m.genre,
        m.duration_minutes,
        m.rating,
        m.language,
        c.cinema_id,
        c.name AS cinema_name,
        c.city,
        sc.screen_id,
        sc.screen_number,
        sc.screen_type,
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
    columns = [col[0] for col in cur.description]
    rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    conn.close()
    return rows

@app.get("/api/screening/{screening_id}/seats")
def get_screening_seats(screening_id: int):
    """Returns the visual 2D seating matrix with real-time booked status."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT s.screening_id, m.title, c.name, sc.screen_number, sc.screen_type,
               s.show_date, s.start_time, s.end_time, s.ticket_price, sc.screen_id, sc.seating_capacity
        FROM screenings s
        JOIN screens sc ON s.screen_id = sc.screen_id
        JOIN cinemas c ON sc.cinema_id = c.cinema_id
        JOIN movies m ON s.movie_id = m.movie_id
        WHERE s.screening_id = ?
    """, (screening_id,))
    show_info = cur.fetchone()
    if not show_info:
        conn.close()
        raise HTTPException(status_code=404, detail="Screening ID not found")
        
    _, title, cinema, screen_num, screen_type, s_date, s_time, e_time, price, screen_id, capacity = show_info
    
    cur.execute("""
        SELECT seat_id, row_label, seat_number, seat_tier, base_price
        FROM seats WHERE screen_id = ?
        ORDER BY row_label, seat_number;
    """, (screen_id,))
    all_seats = cur.fetchall()
    
    cur.execute("""
        SELECT seat_id FROM booked_seats
        WHERE screening_id = ? AND status = 'Booked';
    """, (screening_id,))
    booked_ids = set(r[0] for r in cur.fetchall())
    conn.close()
    
    seat_models = []
    for sid, r_lbl, s_num, tier, b_price in all_seats:
        seat_models.append(SeatModel(
            seat_id=sid,
            row_label=r_lbl,
            seat_number=s_num,
            seat_tier=tier,
            base_price=b_price,
            is_booked=(sid in booked_ids)
        ))
        
    return {
        "screening_id": screening_id,
        "movie_title": title,
        "cinema_name": cinema,
        "screen_number": screen_num,
        "screen_type": screen_type,
        "show_date": s_date,
        "start_time": s_time,
        "end_time": e_time,
        "ticket_price": price,
        "total_seats": capacity,
        "booked_count": len(booked_ids),
        "available_count": capacity - len(booked_ids),
        "seats": seat_models
    }

@app.post("/api/book-tickets", response_model=BookingResponse)
def book_tickets_api(req: BookingRequest):
    """Executes atomic multi-seat booking with SHA-256 digital barcode issuance."""
    if not req.seat_ids:
        raise HTTPException(status_code=400, detail="No seats selected for booking")
        
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN TRANSACTION;")
        
        cur.execute("SELECT ticket_price FROM screenings WHERE screening_id = ?", (req.screening_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Screening does not exist.")
        unit_price = row[0]
        
        # Verify seats availability
        placeholders = ','.join(['?'] * len(req.seat_ids))
        cur.execute(f"""
            SELECT seat_id FROM booked_seats
            WHERE screening_id = ? AND seat_id IN ({placeholders}) AND status = 'Booked'
        """, [req.screening_id] + req.seat_ids)
        clashes = cur.fetchall()
        if clashes:
            raise ValueError(f"Seat(s) {[c[0] for c in clashes]} already booked! Concurrency conflict avoided.")
            
        subtotal = float(unit_price) * len(req.seat_ids)
        discount = 0.0
        if req.promo_code:
            code = req.promo_code.strip().upper()
            if code == "LUXE20":
                discount = round(subtotal * 0.20, 2)
            elif code == "DBMS50":
                discount = min(50.0, subtotal)
                
        total_amount = max(subtotal - discount, 0.0)
        
        cur.execute("""
            INSERT INTO bookings (customer_id, screening_id, total_amount, booking_status)
            VALUES (?, ?, ?, 'Confirmed')
        """, (req.customer_id, req.screening_id, total_amount))
        booking_id = cur.lastrowid
        
        tickets_issued = []
        for sid in req.seat_ids:
            cur.execute("""
                INSERT INTO booked_seats (booking_id, screening_id, seat_id, price, status)
                VALUES (?, ?, ?, ?, 'Booked')
            """, (booking_id, req.screening_id, sid, unit_price))
            booked_seat_id = cur.lastrowid
            
            tkt_number = f"TKT-BKG{booking_id}-S{sid}-{datetime.datetime.now().strftime('%y%m%d%H%M')}"
            raw_hash_data = f"{tkt_number}-{req.screening_id}-{sid}-{datetime.datetime.now().isoformat()}"
            barcode_hash = hashlib.sha256(raw_hash_data.encode()).hexdigest()[:16].upper()
            
            cur.execute("""
                INSERT INTO tickets (booking_id, booked_seat_id, ticket_number, barcode_hash, status)
                VALUES (?, ?, ?, ?, 'Active')
            """, (booking_id, booked_seat_id, tkt_number, barcode_hash))
            tickets_issued.append(TicketIssued(
                ticket_number=tkt_number,
                seat_id=sid,
                barcode_hash=barcode_hash
            ))
            
        txn_ref = f"TXN-{req.payment_method[:3].upper()}-{booking_id}-{datetime.datetime.now().strftime('%H%M%S')}"
        cur.execute("""
            INSERT INTO payments (booking_id, order_id, amount, payment_method, transaction_reference, payment_status)
            VALUES (?, NULL, ?, ?, ?, 'Success')
        """, (booking_id, total_amount, req.payment_method, txn_ref))
        
        conn.commit()
        return BookingResponse(
            booking_id=booking_id,
            subtotal=subtotal,
            discount=discount,
            total_amount=total_amount,
            transaction_reference=txn_ref,
            tickets=tickets_issued
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/api/concessions")
def list_concessions():
    """Lists all food and beverage menu items with real-time stock."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT item_id, item_name, category, unit_price, stock_quantity FROM concession_items ORDER BY category, item_name;")
    columns = [c[0] for c in cur.description]
    items = [dict(zip(columns, r)) for r in cur.fetchall()]
    conn.close()
    return items

@app.post("/api/order-concessions")
def order_concessions_api(req: ConcessionOrderRequest):
    """Processes concession purchases with automated inventory depletion."""
    if not req.items:
        raise HTTPException(status_code=400, detail="Order items list is empty.")
        
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN TRANSACTION;")
        total_order = 0.0
        validated = []
        
        for it in req.items:
            cur.execute("SELECT item_name, unit_price, stock_quantity FROM concession_items WHERE item_id = ?", (it.item_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Concession item ID {it.item_id} not found.")
            name, price, stock = row
            if stock < it.quantity:
                raise ValueError(f"Insufficient stock for '{name}'. Requested: {it.quantity}, Available: {stock}.")
            subtotal = price * it.quantity
            total_order += subtotal
            validated.append((it.item_id, it.quantity, price, subtotal))
            
        cur.execute("""
            INSERT INTO orders (booking_id, customer_id, total_amount, order_status)
            VALUES (?, ?, ?, 'Placed')
        """, (req.booking_id, req.customer_id, total_order))
        order_id = cur.lastrowid
        
        for item_id, qty, price, subtotal in validated:
            cur.execute("""
                INSERT INTO order_items (order_id, item_id, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, item_id, qty, price, subtotal))
            cur.execute("""
                UPDATE concession_items SET stock_quantity = stock_quantity - ? WHERE item_id = ?
            """, (qty, item_id))
            
        txn_ref = f"TXN-CONC-{order_id}-{datetime.datetime.now().strftime('%H%M%S')}"
        cur.execute("""
            INSERT INTO payments (booking_id, order_id, amount, payment_method, transaction_reference, payment_status)
            VALUES (NULL, ?, ?, ?, ?, 'Success')
        """, (order_id, total_order, req.payment_method, txn_ref))
        
        conn.commit()
        return {"order_id": order_id, "total_amount": total_order, "transaction_reference": txn_ref}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.post("/api/cancel-booking")
def cancel_booking_api(req: CancellationRequest):
    """Processes booking cancellation, 10% fee policy, and refund reference."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN TRANSACTION;")
        cur.execute("""
            SELECT b.booking_status, b.total_amount, p.payment_id, p.amount
            FROM bookings b
            JOIN payments p ON b.booking_id = p.booking_id
            WHERE b.booking_id = ? AND p.payment_status = 'Success';
        """, (req.booking_id,))
        res = cur.fetchone()
        if not res:
            raise ValueError(f"Booking #{req.booking_id} not found or payment not finalized.")
        status, total_amt, payment_id, paid_amount = res
        if status == 'Cancelled':
            raise ValueError(f"Booking #{req.booking_id} is already cancelled.")
            
        cancellation_fee = round(paid_amount * 0.10, 2)
        refund_amount = round(paid_amount - cancellation_fee, 2)
        
        cur.execute("UPDATE bookings SET booking_status = 'Cancelled' WHERE booking_id = ?;", (req.booking_id,))
        cur.execute("UPDATE booked_seats SET status = 'Cancelled' WHERE booking_id = ?;", (req.booking_id,))
        cur.execute("UPDATE tickets SET status = 'Cancelled' WHERE booking_id = ?;", (req.booking_id,))
        
        cur.execute("""
            INSERT INTO cancellations (booking_id, reason, cancellation_fee, refund_status)
            VALUES (?, ?, ?, 'Approved');
        """, (req.booking_id, req.reason, cancellation_fee))
        canc_id = cur.lastrowid
        
        refund_ref = f"REF-{req.booking_id}-{datetime.datetime.now().strftime('%H%M%S')}"
        cur.execute("""
            INSERT INTO refunds (cancellation_id, payment_id, refund_amount, refund_reference, status)
            VALUES (?, ?, ?, ?, 'Processed');
        """, (canc_id, payment_id, refund_amount, refund_ref))
        
        conn.commit()
        return {
            "booking_id": req.booking_id,
            "cancellation_fee": cancellation_fee,
            "refund_amount": refund_amount,
            "refund_reference": refund_ref
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.post("/api/validate-ticket")
def validate_ticket_api(req: ValidationRequest):
    """Usher security gate validation tool for cryptographic tickets."""
    token = req.token.strip()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.ticket_id, t.ticket_number, t.barcode_hash, t.status, b.booking_id,
                   m.title, c.name, s.show_date, s.start_time, sc.screen_number
            FROM tickets t
            JOIN bookings b ON t.booking_id = b.booking_id
            JOIN screenings s ON b.screening_id = s.screening_id
            JOIN screens sc ON s.screen_id = sc.screen_id
            JOIN cinemas c ON sc.cinema_id = c.cinema_id
            JOIN movies m ON s.movie_id = m.movie_id
            WHERE t.ticket_number = ? OR t.barcode_hash = ? OR CAST(b.booking_id AS TEXT) = ?
        """, (token, token, token))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No matching ticket or booking found.")
            
        t_id, t_num, b_hash, status, b_id, title, cinema, s_date, s_time, s_num = row
        if status == 'Used':
            return {
                "valid": False,
                "status": "USED",
                "message": f"⚠️ ACCESS DENIED: Ticket #{t_num} has already been checked in!"
            }
        elif status == 'Cancelled':
            return {
                "valid": False,
                "status": "CANCELLED",
                "message": f"❌ ACCESS DENIED: Ticket #{t_num} was cancelled & refunded."
            }
            
        # Mark as Used
        cur.execute("UPDATE tickets SET status = 'Used' WHERE ticket_id = ?", (t_id,))
        conn.commit()
        return {
            "valid": True,
            "status": "ACTIVE_NOW_USED",
            "message": f"✅ ACCESS GRANTED: Welcome to {title}!",
            "details": {
                "ticket_number": t_num,
                "barcode_hash": b_hash,
                "movie": title,
                "cinema": cinema,
                "screen": s_num,
                "showtime": f"{s_date} {s_time}"
            }
        }
    finally:
        conn.close()

@app.get("/api/reports")
def get_executive_reports():
    """Returns analytics from the 5 SQL analytical views."""
    conn = get_connection()
    cur = conn.cursor()
    
    # View 1: Occupancy
    cur.execute("SELECT screening_id, movie_title, cinema_name, screen_number, show_date, start_time, booked_seats, total_seats, occupancy_percentage FROM view_show_occupancy ORDER BY occupancy_percentage DESC;")
    cols1 = [c[0] for c in cur.description]
    occupancy = [dict(zip(cols1, r)) for r in cur.fetchall()]
    
    # View 2: Box Office
    cur.execute("SELECT movie_title, genre, total_screenings, tickets_sold, box_office_gross FROM view_movie_performance ORDER BY box_office_gross DESC;")
    cols2 = [c[0] for c in cur.description]
    box_office = [dict(zip(cols2, r)) for r in cur.fetchall()]
    
    # View 3: Screen Utilization
    cur.execute("SELECT cinema_name, screen_number, screen_type, total_shows_scheduled, operational_hours_runtime, average_capacity_utilization FROM view_screen_utilization;")
    cols3 = [c[0] for c in cur.description]
    screen_util = [dict(zip(cols3, r)) for r in cur.fetchall()]
    
    # View 4: Total Revenue Breakdown
    cur.execute("SELECT cinema_name, ticket_revenue, concession_revenue, cancellation_penalties_retained, total_refunds_disbursed, net_operating_revenue FROM view_total_revenue_breakdown;")
    cols4 = [c[0] for c in cur.description]
    revenue = [dict(zip(cols4, r)) for r in cur.fetchall()]
    
    conn.close()
    return {
        "occupancy": occupancy,
        "box_office": box_office,
        "screen_utilization": screen_util,
        "revenue": revenue
    }

@app.post("/api/diagnostics")
def run_db_diagnostics():
    """Runs automated diagnostic tests verifying all DBMS constraints and triggers."""
    conn = get_connection()
    cur = conn.cursor()
    tests = []
    
    try:
        cur.execute("INSERT INTO booked_seats (booking_id, screening_id, seat_id, price, status) VALUES (1, 1, 1, 350, 'Booked');")
        tests.append({"name": "Double-Booking Prevention", "status": "FAIL", "detail": "Allowed duplicate active seat on same screening"})
    except sqlite3.IntegrityError as e:
        tests.append({"name": "Double-Booking Prevention", "status": "PASS", "detail": f"Enforced via unique index ({e})"})
        
    try:
        cur.execute("INSERT INTO screenings (screen_id, movie_id, show_date, start_time, end_time, ticket_price, status) VALUES (1, 1, '2026-10-04', '11:00:00', '13:00:00', 300, 'Scheduled');")
        tests.append({"name": "Screen Overlap Trigger", "status": "FAIL", "detail": "Allowed overlapping showtime on Screen 1"})
    except sqlite3.IntegrityError as e:
        tests.append({"name": "Screen Overlap Trigger", "status": "PASS", "detail": f"Enforced via trigger ({e})"})
        
    try:
        cur.execute("INSERT INTO order_items (order_id, item_id, quantity, unit_price, subtotal) VALUES (1, 1, -5, 350, -1750);")
        tests.append({"name": "Positive Quantity Check", "status": "FAIL", "detail": "Allowed negative purchase quantity"})
    except sqlite3.IntegrityError as e:
        tests.append({"name": "Positive Quantity Check", "status": "PASS", "detail": f"Enforced via CHECK constraint ({e})"})
        
    try:
        cur.execute("INSERT INTO refunds (cancellation_id, payment_id, refund_amount, refund_reference, status) VALUES (999, 1, 99999.00, 'REF-TEST-OVERFLOW', 'Processed');")
        tests.append({"name": "Refund Limit Enforcement", "status": "FAIL", "detail": "Allowed refund exceeding original payment"})
    except sqlite3.IntegrityError as e:
        tests.append({"name": "Refund Limit Enforcement", "status": "PASS", "detail": f"Enforced via refund limit trigger ({e})"})
        
    conn.rollback()
    conn.close()
    return tests

# -----------------------------------------------------------------------------
# 5. ZERO-BUILD SPA STATIC MOUNT
# -----------------------------------------------------------------------------
STATIC_DIR = os.path.join(BASE_DIR, "static")
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("cinema_server:app", host="0.0.0.0", port=8000, reload=True)
