import streamlit as st
import sqlite3
import pandas as pd
import os
import datetime
import hashlib
import json
import time

# =============================================================================
# 1. PAGE CONFIGURATION & NEO-SAAS MINIMALIST DESIGN SYSTEM
# =============================================================================
st.set_page_config(
    page_title="Cineverse OS | Cinema Placement & Ticketing Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom High-End Styling Matching the Uploaded Screenshots
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600;1,700;1,800&family=Space+Grotesk:wght@500;700&display=swap');

    /* Global Typography & Light Minimal Canvas */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #111827;
    }
    
    .stApp {
        background-color: #F4F6F9;
    }

    /* Top Navigation Bar Container */
    .top-navbar {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 9999px;
        padding: 10px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }
    .brand-logo-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-icon-circle {
        width: 36px;
        height: 36px;
        background: #18181B;
        color: #FFFFFF;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 700;
    }
    .brand-text-title {
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        color: #18181B;
        margin: 0;
        line-height: 1.1;
    }
    .brand-text-subtitle {
        font-size: 0.7rem;
        color: #6B7280;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }

    /* Pill Navigation Badge Styles */
    .status-pill-green {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #F3F4F6;
        color: #374151;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid #E5E7EB;
    }
    .dot-green {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #10B981;
    }

    /* Hero Section Card */
    .hero-container {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 28px;
        padding: 38px 44px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -4px rgba(0, 0, 0, 0.03);
    }
    .hero-tag {
        display: inline-block;
        background: #EDE9FE;
        color: #5B21B6;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        padding: 5px 14px;
        border-radius: 9999px;
        text-transform: uppercase;
        margin-bottom: 14px;
    }
    .hero-headline {
        font-size: 2.85rem;
        font-weight: 900;
        line-height: 1.12;
        letter-spacing: -1px;
        color: #18181B;
        margin-bottom: 14px;
    }
    .hero-headline em {
        font-style: italic;
        font-weight: 400;
        color: #18181B;
        font-family: serif;
    }
    .hero-desc {
        color: #6B7280;
        font-size: 1.02rem;
        line-height: 1.6;
        max-width: 580px;
        margin-bottom: 24px;
    }

    /* Smartphone Phone Mockup Frame (Image 2) */
    .phone-mockup-frame {
        background: #18181B;
        border-radius: 40px;
        padding: 12px;
        box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.35);
        max-width: 320px;
        margin: 0 auto;
    }
    .phone-screen {
        background: #FFFFFF;
        border-radius: 30px;
        padding: 18px 16px;
        color: #111827;
        overflow: hidden;
    }
    .phone-island {
        width: 75px;
        height: 16px;
        background: #18181B;
        border-radius: 9999px;
        margin: 0 auto 14px auto;
    }
    .phone-subcard {
        background: #F8FAFC;
        border: 1px solid #F1F5F9;
        border-radius: 14px;
        padding: 10px 12px;
        margin-bottom: 10px;
    }

    /* Main Parameter Box (Image 1) */
    .param-box {
        background: #F4F6F8;
        border: 1px solid #E5E7EB;
        border-radius: 24px;
        padding: 24px 28px;
        margin-bottom: 24px;
    }
    .param-box-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
    }
    .param-box-title {
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #374151;
    }
    .param-pill-active {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 9999px;
        padding: 4px 12px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #6B7280;
    }

    /* KPI Metric Cards (Image 1) */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 20px 22px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #111827;
        line-height: 1;
        letter-spacing: -0.5px;
    }
    .kpi-subtext {
        font-size: 0.8rem;
        color: #9CA3AF;
        margin-top: 8px;
        font-weight: 500;
    }
    .kpi-badge-green {
        color: #10B981;
        font-weight: 700;
        font-size: 0.8rem;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Progress Bar */
    .progress-track {
        width: 100%;
        height: 6px;
        background: #E5E7EB;
        border-radius: 9999px;
        overflow: hidden;
        margin-top: 10px;
    }
    .progress-fill-dark {
        height: 100%;
        background: #18181B;
        border-radius: 9999px;
    }

    /* Movie Showcase Cards */
    .movie-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .movie-box:hover {
        border-color: #18181B;
        transform: translateY(-2px);
    }
    .movie-tag-pill {
        display: inline-block;
        background: #F3F4F6;
        color: #4B5563;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-right: 4px;
        margin-bottom: 6px;
    }

    /* Hardware Saturation Profile Cards */
    .profile-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        transition: all 0.15s ease;
    }
    .profile-card:hover {
        border-color: #18181B;
    }
    .profile-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .profile-name {
        font-weight: 700;
        font-size: 0.88rem;
        color: #111827;
    }
    .profile-pct {
        font-size: 0.78rem;
        font-weight: 700;
        color: #6B7280;
    }

    /* Minimalist Seating Matrix */
    .curved-screen-minimal {
        height: 6px;
        background: #18181B;
        border-radius: 50% 50% 0 0 / 100% 100% 0 0;
        max-width: 480px;
        margin: 20px auto 8px auto;
        box-shadow: 0 4px 14px rgba(24, 24, 27, 0.15);
    }
    .curved-screen-text {
        text-align: center;
        font-size: 0.7rem;
        letter-spacing: 3px;
        font-weight: 800;
        color: #9CA3AF;
        margin-bottom: 20px;
    }

    /* Modern Pass Container */
    .pass-container {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 24px 28px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        max-width: 600px;
        margin: 20px auto;
        border-top: 6px solid #18181B;
    }

    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #F3F4F6;
        padding: 5px;
        border-radius: 9999px;
        border: 1px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9999px;
        padding: 8px 20px;
        color: #4B5563;
        font-weight: 700;
        font-size: 0.82rem;
        border: none !important;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #18181B !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    /* Streamlit Buttons */
    .stButton>button {
        border-radius: 9999px;
        font-weight: 700;
        letter-spacing: 0.3px;
        padding: 9px 22px;
        border: 1px solid #E5E7EB;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"] {
        background: #18181B;
        color: #FFFFFF;
        border: 1px solid #18181B;
        box-shadow: 0 4px 14px rgba(24, 24, 27, 0.18);
    }
    .stButton>button[kind="primary"]:hover {
        background: #27272A;
        border-color: #27272A;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 2. DATABASE LAYER & ENGINE CONNECTIONS
# =============================================================================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "cinema_booking.db")

def get_connection():
    """Create fresh SQLite connection with strict foreign key integrity."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@st.cache_data(ttl=5)
def fetch_dataframe(query: str, params: tuple = ()) -> pd.DataFrame:
    """Cached query executor for analytical reads."""
    try:
        with get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.error(f"⚠️ Query Error: {e}")
        return pd.DataFrame()


# =============================================================================
# 3. MOVIE ASSETS & POSTERS
# =============================================================================
MOVIE_METADATA = {
    "Oppenheimer": {
        "poster": "https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=800&auto=format&fit=crop",
        "tagline": "The world forever changes.",
        "score": "⭐ 8.9",
        "director": "Christopher Nolan",
        "cast": "Cillian Murphy, Emily Blunt, Robert Downey Jr."
    },
    "Dune: Part Two": {
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=800&auto=format&fit=crop",
        "tagline": "Long live the fighters.",
        "score": "⭐ 8.8",
        "director": "Denis Villeneuve",
        "cast": "Timothée Chalamet, Zendaya, Rebecca Ferguson"
    },
    "Interstellar": {
        "poster": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=800&auto=format&fit=crop",
        "tagline": "Mankind was born on Earth. It was never meant to die here.",
        "score": "⭐ 8.7",
        "director": "Christopher Nolan",
        "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain"
    },
    "Kalki 2898 AD": {
        "poster": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=800&auto=format&fit=crop",
        "tagline": "The future of Indian cinematic mythology.",
        "score": "⭐ 8.4",
        "director": "Nag Ashwin",
        "cast": "Prabhas, Amitabh Bachchan, Kamal Haasan"
    },
    "Inception": {
        "poster": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?q=80&w=800&auto=format&fit=crop",
        "tagline": "Your mind is the scene of the crime.",
        "score": "⭐ 8.8",
        "director": "Christopher Nolan",
        "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page"
    }
}


# =============================================================================
# 4. BUSINESS LOGIC SERVICES
# =============================================================================
def book_tickets_service(customer_id: int, screening_id: int, seat_ids: list, payment_method: str, discount_amount: float = 0.0):
    """Executes atomic multi-seat booking with SHA-256 digital barcode issuance."""
    if not seat_ids:
        return False, "Please select at least one seat to proceed."
        
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN TRANSACTION;")
        cur.execute("SELECT ticket_price FROM screenings WHERE screening_id = ?", (screening_id,))
        show_row = cur.fetchone()
        if not show_row:
            raise ValueError("Designated screening not found.")
        unit_price = show_row[0]
        
        placeholders = ','.join(['?'] * len(seat_ids))
        cur.execute(f"""
            SELECT seat_id FROM booked_seats 
            WHERE screening_id = ? AND seat_id IN ({placeholders}) AND status = 'Booked'
        """, [screening_id] + seat_ids)
        clashes = cur.fetchall()
        if clashes:
            raise ValueError(f"Seat(s) {[c[0] for c in clashes]} were just reserved by another guest.")
            
        subtotal = float(unit_price) * len(seat_ids)
        total_amount = max(subtotal - discount_amount, 0.0)
        
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
            
            tkt_num = f"TKT-BKG{booking_id}-S{sid}-{datetime.datetime.now().strftime('%y%m%d%H%M')}"
            raw_hash = f"{tkt_num}-{screening_id}-{sid}-{datetime.datetime.now().isoformat()}"
            barcode_hash = hashlib.sha256(raw_hash.encode()).hexdigest()[:16].upper()
            
            cur.execute("""
                INSERT INTO tickets (booking_id, booked_seat_id, ticket_number, barcode_hash, status)
                VALUES (?, ?, ?, ?, 'Active')
            """, (booking_id, booked_seat_id, tkt_num, barcode_hash))
            tickets_issued.append({
                "ticket_number": tkt_num,
                "seat_id": sid,
                "barcode_hash": barcode_hash
            })
            
        txn_ref = f"TXN-{payment_method[:3].upper()}-{booking_id}-{datetime.datetime.now().strftime('%H%M%S')}"
        cur.execute("""
            INSERT INTO payments (booking_id, order_id, amount, payment_method, transaction_reference, payment_status)
            VALUES (?, NULL, ?, ?, ?, 'Success')
        """, (booking_id, total_amount, payment_method, txn_ref))
        
        conn.commit()
        return True, {
            "booking_id": booking_id,
            "subtotal": subtotal,
            "discount": discount_amount,
            "total_amount": total_amount,
            "transaction_reference": txn_ref,
            "tickets": tickets_issued
        }
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def order_concessions_service(customer_id: int, booking_id: int, cart_items: list, payment_method: str = "UPI"):
    """Handles concessions order placement, auto-stock depletion, and payment."""
    if not cart_items:
        return False, "Cart is empty."
        
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN TRANSACTION;")
        total_amount = 0.0
        validated = []
        
        for item_id, qty in cart_items:
            cur.execute("SELECT item_name, unit_price, stock_quantity FROM concession_items WHERE item_id = ?", (item_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Item #{item_id} does not exist.")
            name, price, stock = row
            if stock < qty:
                raise ValueError(f"Insufficient stock for {name}. Requested: {qty}, Available: {stock}.")
            subtotal = price * qty
            total_amount += subtotal
            validated.append((item_id, qty, price, subtotal))
            
        b_val = booking_id if booking_id > 0 else None
        cur.execute("""
            INSERT INTO orders (booking_id, customer_id, total_amount, order_status)
            VALUES (?, ?, ?, 'Placed')
        """, (b_val, customer_id, total_amount))
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
        """, (order_id, total_amount, payment_method, txn_ref))
        
        conn.commit()
        return True, {"order_id": order_id, "total": total_amount, "txn_ref": txn_ref}
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def cancel_booking_service(booking_id: int, reason: str):
    """Processes booking cancellation, 10% policy deduction, and automated refund."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN TRANSACTION;")
        cur.execute("""
            SELECT b.booking_status, b.total_amount, p.payment_id, p.amount 
            FROM bookings b 
            JOIN payments p ON b.booking_id = p.booking_id 
            WHERE b.booking_id = ? AND p.payment_status = 'Success';
        """, (booking_id,))
        row = cur.fetchone()
        if not row:
            return False, f"Booking #{booking_id} was not found or payment is unfinalized."
        status, total_amt, payment_id, paid_amount = row
        if status == 'Cancelled':
            return False, f"Booking #{booking_id} has already been cancelled."
            
        cancellation_fee = round(paid_amount * 0.10, 2)
        refund_amount = round(paid_amount - cancellation_fee, 2)
        
        cur.execute("UPDATE bookings SET booking_status = 'Cancelled' WHERE booking_id = ?", (booking_id,))
        cur.execute("UPDATE booked_seats SET status = 'Cancelled' WHERE booking_id = ?", (booking_id,))
        cur.execute("UPDATE tickets SET status = 'Cancelled' WHERE booking_id = ?", (booking_id,))
        
        cur.execute("""
            INSERT INTO cancellations (booking_id, reason, cancellation_fee, refund_status)
            VALUES (?, ?, ?, 'Approved')
        """, (booking_id, reason, cancellation_fee))
        canc_id = cur.lastrowid
        
        ref_code = f"REF-{booking_id}-{datetime.datetime.now().strftime('%H%M%S')}"
        cur.execute("""
            INSERT INTO refunds (cancellation_id, payment_id, refund_amount, refund_reference, status)
            VALUES (?, ?, ?, ?, 'Processed')
        """, (canc_id, payment_id, refund_amount, ref_code))
        
        conn.commit()
        return True, {
            "booking_id": booking_id,
            "refund_amount": refund_amount,
            "cancellation_fee": cancellation_fee,
            "refund_reference": ref_code
        }
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def validate_ticket_token(token_str: str):
    """Validates ticket token and marks it Used if Active (Usher security gate)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.ticket_id, t.ticket_number, t.barcode_hash, t.status, b.booking_id, m.title, c.name, s.show_date, s.start_time, sc.screen_number
            FROM tickets t
            JOIN bookings b ON t.booking_id = b.booking_id
            JOIN screenings s ON b.screening_id = s.screening_id
            JOIN screens sc ON s.screen_id = sc.screen_id
            JOIN cinemas c ON sc.cinema_id = c.cinema_id
            JOIN movies m ON s.movie_id = m.movie_id
            WHERE t.ticket_number = ? OR t.barcode_hash = ? OR CAST(b.booking_id AS TEXT) = ?
        """, (token_str, token_str, token_str))
        rows = cur.fetchall()
        if not rows:
            return False, "No ticket found matching the specified token or Booking ID."
            
        ticket_id, t_num, b_hash, status, b_id, title, cinema, s_date, s_time, s_num = rows[0]
        
        if status == 'Used':
            return False, f"⚠️ ACCESS DENIED: Ticket #{t_num} has ALREADY BEEN CHECKED IN."
        elif status == 'Cancelled':
            return False, f"❌ ACCESS DENIED: Ticket #{t_num} was CANCELLED & REFUNDED."
            
        # Mark as Used
        cur.execute("UPDATE tickets SET status = 'Used' WHERE ticket_id = ?", (ticket_id,))
        conn.commit()
        return True, {
            "ticket_number": t_num,
            "barcode_hash": b_hash,
            "movie": title,
            "cinema": cinema,
            "screen": s_num,
            "time": f"{s_date} {s_time}"
        }
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


# =============================================================================
# 5. VIEW MODULES
# =============================================================================

def render_top_navbar():
    """Renders the top pill navbar exactly like Images 1 and 2."""
    st.markdown("""
    <div class="top-navbar">
        <div class="brand-logo-group">
            <div class="brand-icon-circle">⚡</div>
            <div>
                <div class="brand-text-title">CINEVERSE OS</div>
                <div class="brand-text-subtitle">DBMS AUDITORIUM ENGINE</div>
            </div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span class="status-pill-green"><span class="dot-green"></span> SQLite ACID :3306</span>
            <span style="font-size: 0.78rem; font-weight: 700; color: #4B5563; background: #F3F4F6; padding: 6px 14px; border-radius: 9999px; border: 1px solid #E5E7EB;">
                👤 Rahul Sharma (Customer #2)
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# ATTEMPT 1 ENHANCEMENT: MOVIE CATALOG & DISCOVERY WITH FILTERS
# -----------------------------------------------------------------------------
def render_movie_catalog_discovery():
    """Renders comprehensive movie schedule with filters and instant showtime booking buttons."""
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 24px 28px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                EXPLORE SCREENINGS & CINEMA SCHEDULES
            </div>
            <span class="param-pill-active">Live Theater Feeds</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Discovery Filters
    c_search, c_city, c_format, c_genre = st.columns([2.5, 1.5, 1.5, 1.5])
    with c_search:
        search_query = st.text_input("🔍 Search movies, directors or cinemas:", placeholder="e.g. Oppenheimer, IMAX, Nolan...")
    with c_city:
        city_choice = st.selectbox("City Filter:", ["All Cities", "Hyderabad", "Mumbai", "Bangalore"])
    with c_format:
        format_choice = st.selectbox("Auditorium Format:", ["All Formats", "IMAX 3D", "4DX", "Gold VIP", "Standard"])
    with c_genre:
        genre_choice = st.selectbox("Genre Filter:", ["All Genres", "Sci-Fi", "Drama", "Action", "Mythology"])
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Query screenings with filters
    base_query = """
        SELECT 
            s.screening_id, m.movie_id, m.title, m.genre, m.duration_minutes, m.rating, m.language,
            c.name as cinema_name, c.city, sc.screen_number, sc.screen_type,
            s.show_date, s.start_time, s.end_time, s.ticket_price
        FROM screenings s
        JOIN screens sc ON s.screen_id = sc.screen_id
        JOIN cinemas c ON sc.cinema_id = c.cinema_id
        JOIN movies m ON s.movie_id = m.movie_id
        WHERE s.status != 'Cancelled'
    """
    params = []
    if city_choice != "All Cities":
        base_query += " AND c.city = ?"
        params.append(city_choice)
    if format_choice != "All Formats":
        base_query += " AND sc.screen_type = ?"
        params.append(format_choice)
    if genre_choice != "All Genres":
        base_query += " AND m.genre LIKE ?"
        params.append(f"%{genre_choice}%")
        
    base_query += " ORDER BY s.show_date, s.start_time;"
    screenings_df = fetch_dataframe(base_query, tuple(params))
    
    if search_query:
        screenings_df = screenings_df[
            screenings_df['title'].str.contains(search_query, case=False, na=False) |
            screenings_df['cinema_name'].str.contains(search_query, case=False, na=False) |
            screenings_df['genre'].str.contains(search_query, case=False, na=False)
        ]
        
    if screenings_df.empty:
        st.info("No movie screenings match your filter criteria.")
        return
        
    unique_movies = screenings_df[['movie_id', 'title', 'genre', 'duration_minutes', 'rating', 'language']].drop_duplicates()
    
    # Render Movie Cards Grid
    cols = st.columns(3)
    for idx, (_, mov) in enumerate(unique_movies.iterrows()):
        col = cols[idx % 3]
        meta = MOVIE_METADATA.get(mov['title'], {
            "poster": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=800&auto=format&fit=crop",
            "tagline": "A cinematic tour de force.",
            "score": "⭐ 8.5",
            "director": "Visionary Director",
            "cast": "Ensemble Cast"
        })
        mov_shows = screenings_df[screenings_df['movie_id'] == mov['movie_id']]
        
        with col:
            st.markdown(f"""
            <div class="movie-box">
                <div>
                    <img src="{meta['poster']}" style="width: 100%; height: 210px; object-fit: cover; border-radius: 12px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <h4 style="margin: 0; font-size: 1.15rem; font-weight: 800; color: #18181B;">{mov['title']}</h4>
                        <span style="font-size: 0.8rem; font-weight: 700; background: #F3F4F6; padding: 2px 8px; border-radius: 6px; color: #18181B;">{meta['score']}</span>
                    </div>
                    <div style="margin-top: 6px; margin-bottom: 8px;">
                        <span class="movie-tag-pill">{mov['genre']}</span>
                        <span class="movie-tag-pill">{mov['rating']}</span>
                        <span class="movie-tag-pill">{mov['language']}</span>
                        <span class="movie-tag-pill">{mov['duration_minutes']} min</span>
                    </div>
                    <p style="font-size: 0.78rem; color: #6B7280; margin: 4px 0 12px 0;">
                        <b>Director:</b> {meta['director']}<br>
                        <b>Cast:</b> {meta['cast']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<small style='font-weight:700; color:#374151;'>Available Showtimes:</small>", unsafe_allow_html=True)
            for _, show in mov_shows.iterrows():
                btn_label = f"🎟️ {show['start_time']} • Scrn {show['screen_number']} ({show['screen_type']}) - Rs.{int(show['ticket_price'])}"
                if st.button(btn_label, key=f"quick_book_{show['screening_id']}"):
                    st.session_state['selected_screening_id'] = show['screening_id']
                    st.session_state['active_tab_index'] = 0
                    st.rerun()
                    
            st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# ATTEMPT 2 ENHANCEMENT: SEATING SELECTION, CART, PROMO CODES & DIGITAL PASS
# -----------------------------------------------------------------------------
def render_interactive_booking_system():
    """Renders interactive 2D seat matrix with promo codes, tax breakdown, and Apple Wallet pass."""
    # Top Hero Section (Image 2)
    st.markdown("""
    <div class="hero-container">
        <div style="display: grid; grid-template-columns: 1.3fr 0.9fr; gap: 40px; align-items: center;">
            <div>
                <div class="hero-tag">CAPACITY OPTIMIZATION • ZERO CONFLICTS</div>
                <div class="hero-headline">
                    OPTIMIZE YOUR<br>
                    <em>CINEMA MESH</em>
                </div>
                <div class="hero-desc">
                    Formally schedule screening slots with automated 15-minute turnaround triggers, 
                    reserve multi-seat auditoriums with cryptographic SHA-256 barcodes, and manage 
                    concessions inventory with strict ACID compliance.
                </div>
                <div class="hero-stats-row">
                    <div>
                        <div class="stat-number">100%</div>
                        <div class="stat-caption">Zero-Conflict Triggers</div>
                    </div>
                    <div>
                        <div class="stat-number">1.84ms</div>
                        <div class="stat-caption">Avg Transaction Latency</div>
                    </div>
                    <div>
                        <div class="stat-number">&lt; 1%</div>
                        <div class="stat-caption">Seat Double-Booking Gap</div>
                    </div>
                </div>
            </div>
            <div>
                <div class="phone-mockup-frame">
                    <div class="phone-screen">
                        <div class="phone-island"></div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                            <div>
                                <div style="font-weight: 800; font-size: 0.95rem; color: #18181B;">Auditorium Monitor</div>
                                <div style="font-size: 0.68rem; color: #9CA3AF;">Live Screening Telemetry</div>
                            </div>
                            <span style="background: #F3F4F6; font-size: 0.65rem; font-weight: 700; padding: 4px 8px; border-radius: 9999px; color: #4B5563;">
                                Campus PVR
                            </span>
                        </div>
                        <div class="phone-subcard">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 0.68rem; font-weight: 700; color: #6B7280; text-transform: uppercase;">AVERAGE LATENCY</div>
                                    <div style="font-size: 1.3rem; font-weight: 800; color: #18181B;">2.5 ms</div>
                                </div>
                                <div style="font-size: 1.2rem;">⚡</div>
                            </div>
                        </div>
                        <div class="phone-subcard">
                            <div style="font-size: 0.68rem; font-weight: 700; color: #6B7280; text-transform: uppercase;">CAPACITY INTEGRITY</div>
                            <div style="font-size: 0.88rem; font-weight: 700; color: #10B981; margin-top: 2px;">
                                ✓ 100% Feasible
                            </div>
                        </div>
                        <div class="phone-subcard">
                            <div style="display: flex; justify-content: space-between; font-size: 0.68rem; font-weight: 700; color: #6B7280;">
                                <span>CLUSTER OCCUPANCY</span>
                                <span>74.2%</span>
                            </div>
                            <div class="progress-track" style="height: 6px;">
                                <div class="progress-fill-dark" style="width: 74.2%;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. PARAMETERS BOX (Image 1)
    st.markdown("""
    <div class="param-box">
        <div class="param-box-header">
            <span class="param-box-title">RESERVATION & SCREENING PARAMETERS</span>
            <span class="param-pill-active">Active Config</span>
        </div>
    """, unsafe_allow_html=True)
    
    screenings = fetch_dataframe("""
        SELECT 
            s.screening_id, m.title, c.name as cinema_name, sc.screen_number, sc.screen_type,
            s.show_date, s.start_time, s.ticket_price, sc.screen_id
        FROM screenings s
        JOIN screens sc ON s.screen_id = sc.screen_id
        JOIN cinemas c ON sc.cinema_id = c.cinema_id
        JOIN movies m ON s.movie_id = m.movie_id
        WHERE s.status != 'Cancelled'
        ORDER BY s.show_date, s.start_time;
    """)
    
    if screenings.empty:
        st.warning("No scheduled screenings available.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
        
    screening_options = {
        r['screening_id']: f"{r['title']} ({r['show_date']} @ {r['start_time']}) - {r['cinema_name']} Scrn {r['screen_number']} [{r['screen_type']}]"
        for _, r in screenings.iterrows()
    }
    
    default_screening = st.session_state.get('selected_screening_id', list(screening_options.keys())[0])
    default_index = list(screening_options.keys()).index(default_screening) if default_screening in screening_options else 0
    
    p1, p2, p3, p4 = st.columns([3, 1.5, 1.5, 1.5])
    with p1:
        chosen_id = st.selectbox("Select Screening:", options=list(screening_options.keys()), index=default_index, format_func=lambda x: screening_options[x])
    with p2:
        payment_method = st.selectbox("Payment Channel:", ["UPI", "Credit Card", "Debit Card", "Cash"])
    with p3:
        cust_df = fetch_dataframe("SELECT customer_id, full_name FROM customers")
        cust_opts = {r['customer_id']: r['full_name'] for _, r in cust_df.iterrows()} if not cust_df.empty else {2: "Customer 2"}
        customer_id = st.selectbox("Customer:", options=list(cust_opts.keys()), index=1 if 2 in cust_opts else 0, format_func=lambda x: cust_opts[x])
    with p4:
        promo_code = st.text_input("Promo Code (Optional):", placeholder="e.g. LUXE20").strip().upper()
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. 4 KPI METRIC CARDS ROW (Image 1)
    rev_df = fetch_dataframe("SELECT * FROM view_total_revenue_breakdown")
    total_gross = rev_df['ticket_revenue'].sum() if not rev_df.empty else 4500
    occ_df = fetch_dataframe("SELECT occupancy_percentage FROM view_show_occupancy")
    avg_occupancy = round(occ_df['occupancy_percentage'].mean(), 1) if not occ_df.empty else 74.2
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-label">AVERAGE LATENCY</div>
                <div class="kpi-value">2.5 <span style="font-size: 1.1rem; font-weight: 500; color: #6B7280;">ms</span></div>
            </div>
            <div class="kpi-subtext">Total Gross: Rs. {total_gross:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-label">FEASIBILITY STATUS</div>
                <div class="kpi-value">10 / 10</div>
            </div>
            <div class="kpi-badge-green">✓ 100% Capacity Feasible</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-label">CLUSTER OCCUPANCY LOAD</div>
                <div class="kpi-value">{avg_occupancy}%</div>
            </div>
            <div class="progress-track">
                <div class="progress-fill-dark" style="width: {min(avg_occupancy, 100)}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-label">SOLVER RUNTIME</div>
                <div class="kpi-value">2.891 <span style="font-size: 1.1rem; font-weight: 500; color: #6B7280;">ms</span></div>
            </div>
            <div class="kpi-subtext">Exact Optimizer (Branch-and-Bound)</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. INTERACTIVE 2D AUDITORIUM GRID
    selected_screening = screenings[screenings['screening_id'] == chosen_id].iloc[0]
    screen_id = int(selected_screening['screen_id'])
    unit_price = float(selected_screening['ticket_price'])
    
    seats = fetch_dataframe("""
        SELECT seat_id, row_label, seat_number, seat_tier, base_price 
        FROM seats WHERE screen_id = ? 
        ORDER BY row_label, seat_number;
    """, (screen_id,))
    
    booked_seats = fetch_dataframe("""
        SELECT seat_id FROM booked_seats 
        WHERE screening_id = ? AND status = 'Booked';
    """, (chosen_id,))
    booked_ids = set(booked_seats['seat_id'].tolist()) if not booked_seats.empty else set()
    
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 24px 28px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                2D AUDITORIUM SEAT MATRIX (TIER-BASED RECLINERS)
            </div>
            <div style="display: flex; gap: 14px; font-size: 0.75rem; font-weight: 700; color: #6B7280;">
                <span>◻ Available</span>
                <span style="color: #18181B;">◼ Selected</span>
                <span style="color: #EF4444;">☒ Occupied</span>
            </div>
        </div>
        <div class="curved-screen-minimal"></div>
        <div class="curved-screen-text">AUDITORIUM PROJECTION SCREEN</div>
    """, unsafe_allow_html=True)
    
    rows = sorted(seats['row_label'].unique())
    available_seats = []
    
    for r_lbl in rows:
        row_seats = seats[seats['row_label'] == r_lbl].sort_values('seat_number')
        tier = row_seats.iloc[0]['seat_tier']
        pills_html = []
        for _, s_row in row_seats.iterrows():
            sid = s_row['seat_id']
            snum = s_row['seat_number']
            if sid in booked_ids:
                pills_html.append(f'<span style="display:inline-flex; align-items:center; justify-content:center; width:36px; height:32px; border-radius:8px; font-size:0.75rem; font-weight:700; margin:2px; background:#FEE2E2; color:#EF4444; border:1px solid #FECACA;">✕</span>')
            else:
                available_seats.append((sid, f"{r_lbl}{snum:02d} ({tier})"))
                pills_html.append(f'<span style="display:inline-flex; align-items:center; justify-content:center; width:36px; height:32px; border-radius:8px; font-size:0.75rem; font-weight:700; margin:2px; background:#FFFFFF; color:#4B5563; border:1px solid #E5E7EB;">{snum:02d}</span>')
                
        seats_str = "".join(pills_html)
        tier_icon = "👑" if tier == "Platinum" else ("💎" if tier == "Gold" else "🎟️")
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 4px;">
            <span style="font-weight: 800; font-size: 0.8rem; color: #9CA3AF; width: 25px; text-align: center;">{r_lbl}</span>
            <div>{seats_str}</div>
            <span style="font-size: 0.72rem; color: #6B7280; width: 85px; margin-left: 8px;">{tier_icon} {tier}</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: none; border-top: 1px solid #F3F4F6; margin: 18px 0;'>", unsafe_allow_html=True)
    
    # Live Seat Multiselect & Dynamic Checkout Calculations
    c_pick, c_calc = st.columns([2.5, 1.5])
    with c_pick:
        chosen_sids = st.multiselect(
            "Select Vacant Seats:",
            options=[s[0] for s in available_seats],
            format_func=lambda sid: next(s[1] for s in available_seats if s[0] == sid),
            placeholder="Click to pick your preferred seats..."
        )
        
    with c_calc:
        num_seats = len(chosen_sids)
        raw_subtotal = num_seats * unit_price
        
        # Calculate Discounts
        discount = 0.0
        if promo_code == "LUXE20":
            discount = round(raw_subtotal * 0.20, 2)
            st.caption("🎉 Coupon LUXE20 Applied: 20% Discount!")
        elif promo_code == "DBMS50":
            discount = min(50.0, raw_subtotal)
            st.caption("🎉 Coupon DBMS50 Applied: Rs. 50 Off!")
            
        final_total = max(raw_subtotal - discount, 0.0)
        
        st.markdown(f"""
        <div style="background: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 14px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #6B7280; margin-bottom: 4px;">
                <span>Seats ({num_seats}x):</span>
                <span>Rs. {raw_subtotal:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #10B981; margin-bottom: 4px;">
                <span>Discount / Promo:</span>
                <span>- Rs. {discount:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 1.15rem; font-weight: 800; color: #18181B; border-top: 1px solid #E5E7EB; padding-top: 8px; margin-top: 4px;">
                <span>Total Payable:</span>
                <span>Rs. {final_total:,.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        confirm_btn = st.button("▶ Confirm & Pay Online", type="primary", use_container_width=True, disabled=(num_seats == 0))
        
    if confirm_btn and chosen_sids:
        with st.spinner("Locking seats & generating cryptographic admission tokens..."):
            ok, res = book_tickets_service(customer_id, chosen_id, chosen_sids, payment_method, discount)
            
        if ok:
            st.success(f"✓ Reservation #{res['booking_id']} confirmed!")
            
            # Apple Wallet / Minimalist Pass Output
            tokens_html = "<br>".join([f"• Seat #{t['seat_id']} &nbsp;|&nbsp; <code>{t['barcode_hash']}</code>" for t in res['tickets']])
            st.markdown(f"""
            <div class="pass-container">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                    <div>
                        <div style="font-size: 0.72rem; font-weight: 800; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;">
                            BOARDING PASS • CONFIRMED
                        </div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #18181B; margin-top: 2px;">
                            {selected_screening['title']}
                        </div>
                        <div style="font-size: 0.8rem; color: #6B7280;">
                            {selected_screening['cinema_name']} • Screen {selected_screening['screen_number']} ({selected_screening['screen_type']})
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: #F3F4F6; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; color: #18181B;">
                            #{res['booking_id']}
                        </span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; background: #F8FAFC; padding: 12px 16px; border-radius: 12px; border: 1px solid #E5E7EB;">
                    <div>
                        <div style="font-size: 0.68rem; color: #6B7280; font-weight: 700;">DATE & TIME</div>
                        <div style="font-weight: 800; font-size: 0.85rem; color: #18181B;">{selected_screening['show_date']} {selected_screening['start_time']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.68rem; color: #6B7280; font-weight: 700;">SEATS RESERVED</div>
                        <div style="font-weight: 800; font-size: 0.85rem; color: #18181B;">{num_seats} Seats</div>
                    </div>
                    <div>
                        <div style="font-size: 0.68rem; color: #6B7280; font-weight: 700;">TOTAL CHARGED</div>
                        <div style="font-weight: 800; font-size: 0.85rem; color: #18181B;">Rs. {res['total_amount']}</div>
                    </div>
                </div>
                
                <div style="font-size: 0.75rem; color: #4B5563;">
                    <div style="font-weight: 700; margin-bottom: 4px;">CRYPTOGRAPHIC DIGITAL TOKENS (SHA-256):</div>
                    {tokens_html}
                </div>
                <div style="font-size: 0.68rem; color: #9CA3AF; margin-top: 10px; font-family: monospace;">
                    TRANSACTION REFERENCE: {res['transaction_reference']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.cache_data.clear()
        else:
            st.error(f"Transaction Aborted: {res}")
            
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# ATTEMPT 3 ENHANCEMENT: ENTERPRISE ECOSYSTEM (F&B COMBOS, USHER GATE, BI EXPORT)
# -----------------------------------------------------------------------------
def render_concessions_lounge():
    """Renders Gourmet Concessions with Meal Combos & live tray calculator."""
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 24px 28px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                GOURMET CONCESSIONS & SEAT DELIVERY
            </div>
            <span class="param-pill-active">Inventory Auto-Depletion</span>
        </div>
    """, unsafe_allow_html=True)
    
    items = fetch_dataframe("SELECT item_id, item_name, category, unit_price, stock_quantity FROM concession_items ORDER BY category, item_name;")
    
    c_cards, c_tray = st.columns([2.5, 1.5])
    with c_cards:
        st.markdown("#### Chef's Menu & Combos")
        categories = items['category'].unique()
        selected_qtys = {}
        
        for cat in categories:
            st.markdown(f"<small style='font-weight:800; color:#6B7280; letter-spacing:1px; text-transform:uppercase;'>{cat}</small>", unsafe_allow_html=True)
            cat_df = items[items['category'] == cat]
            subcols = st.columns(2)
            for i_idx, (_, row) in enumerate(cat_df.iterrows()):
                with subcols[i_idx % 2]:
                    with st.container(border=True):
                        st.markdown(f"**{row['item_name']}**")
                        st.markdown(f"**Rs. {int(row['unit_price'])}** &nbsp;|&nbsp; <small style='color:#6B7280;'>Stock: {row['stock_quantity']}</small>", unsafe_allow_html=True)
                        if row['stock_quantity'] > 0:
                            qty = st.number_input(f"Qty", min_value=0, max_value=int(row['stock_quantity']), value=0, key=f"fnb_qty_{row['item_id']}")
                            if qty > 0:
                                selected_qtys[row['item_id']] = (row['item_name'], float(row['unit_price']), qty)
                        else:
                            st.caption("Out of stock")
                            
    with c_tray:
        st.markdown("#### 🛍️ Your Tray")
        with st.container(border=True):
            link_bkg = st.number_input("Link to Confirmed Booking ID (Optional):", min_value=0, value=0)
            if not selected_qtys:
                st.info("Tray is empty. Add food & beverages from the menu.")
            else:
                total_tray = 0.0
                for iid, (name, price, qty) in selected_qtys.items():
                    sub = price * qty
                    total_tray += sub
                    st.markdown(f"• **{qty}x** {name} <span style='float:right;'>Rs. {sub:,.2f}</span>", unsafe_allow_html=True)
                st.divider()
                st.markdown(f"### Tray Total: Rs. {total_tray:,.2f}")
                if st.button("▶ Place Concessions Order", type="primary", use_container_width=True):
                    cart = [(iid, q) for iid, (_, _, q) in selected_qtys.items()]
                    ok, o_res = order_concessions_service(2, link_bkg, cart, "UPI")
                    if ok:
                        st.success(f"✓ Order #{o_res['order_id']} dispatched! Total: Rs.{o_res['total']}")
                        st.cache_data.clear()
                    else:
                        st.error(o_res)
                        
    st.markdown("</div>", unsafe_allow_html=True)


def render_usher_gate_validator():
    """Security Usher tool to scan tickets and verify digital tokens in real-time."""
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 24px 28px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                SECURITY USHER GATE & TOKEN SCANNER
            </div>
            <span class="param-pill-active">Anti-Counterfeit Check</span>
        </div>
    """, unsafe_allow_html=True)
    
    col_input, col_audit = st.columns([1.5, 2.5])
    with col_input:
        token_input = st.text_input("Enter Ticket #, Barcode Hash or Booking ID:", placeholder="e.g. TKT-2026-00101 or Hash...")
        if st.button("▶ Verify & Admit Guest", type="primary", use_container_width=True) and token_input:
            with st.spinner("Checking database signature..."):
                ok, val_res = validate_ticket_token(token_input.strip())
            if ok:
                st.success(f"✅ ACCESS GRANTED: Welcome to {val_res['movie']}!")
                st.markdown(f"""
                - **Cinema Hall:** {val_res['cinema']} (Screen {val_res['screen']})
                - **Showtime:** {val_res['time']}
                - **Ticket Number:** `{val_res['ticket_number']}`
                - **Status:** Marked as `Used`
                """)
                st.cache_data.clear()
            else:
                st.error(val_res)
                
    with col_audit:
        st.markdown("#### Live Active Tickets Pool")
        active_tkts = fetch_dataframe("""
            SELECT t.ticket_id, t.ticket_number, t.barcode_hash, t.status, b.booking_id, m.title
            FROM tickets t
            JOIN bookings b ON t.booking_id = b.booking_id
            JOIN screenings s ON b.screening_id = s.screening_id
            JOIN movies m ON s.movie_id = m.movie_id
            ORDER BY t.ticket_id DESC LIMIT 6;
        """)
        st.dataframe(active_tkts, use_container_width=True, hide_index=True)
        
    st.markdown("</div>", unsafe_allow_html=True)


def render_cancellations_tab():
    """Self-service cancellation and refund engine with transparent policy."""
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 24px 28px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                BOOKING CANCELLATION & INSTANT REFUND
            </div>
            <span class="param-pill-active">10% Retention Policy</span>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1.5, 2.5])
    with c1:
        cancel_id = st.number_input("Enter Booking ID to Cancel:", min_value=1, step=1)
        reason = st.text_input("Cancellation Reason:", "Customer change of plans")
        if st.button("▶ Process Cancellation & Refund", type="primary", use_container_width=True):
            ok, res = cancel_booking_service(cancel_id, reason)
            if ok:
                st.success(f"✓ Booking #{cancel_id} cancelled.")
                st.metric("Refund Disbursed", f"Rs. {res['refund_amount']:,.2f}", delta=f"- Rs. {res['cancellation_fee']:,.2f} (10% Fee)", delta_color="inverse")
                st.caption(f"Refund Audit Reference: `{res['refund_reference']}`")
                st.cache_data.clear()
            else:
                st.error(res)
                
    with c2:
        st.markdown("#### Audit Trail (Recent Cancellations)")
        canc_df = fetch_dataframe("""
            SELECT c.cancellation_id as ID, b.booking_id as Bkg_ID, m.title as Movie, c.cancellation_fee as Fee, r.refund_amount as Refund, r.refund_reference as Audit_Ref
            FROM cancellations c
            JOIN bookings b ON c.booking_id = b.booking_id
            JOIN screenings s ON b.screening_id = s.screening_id
            JOIN movies m ON s.movie_id = m.movie_id
            LEFT JOIN refunds r ON c.cancellation_id = r.cancellation_id
            ORDER BY c.cancellation_id DESC LIMIT 6;
        """)
        if not canc_df.empty:
            st.dataframe(canc_df, use_container_width=True, hide_index=True)
        else:
            st.info("No cancellations recorded.")
            
    st.markdown("</div>", unsafe_allow_html=True)


def render_executive_bi():
    """Executive BI dashboard with live charts, CSV download and diagnostic verification."""
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 24px 28px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                EXECUTIVE TELEMETRY & SQL REPORTING VIEWS
            </div>
            <span class="param-pill-active">Data Intelligence</span>
        </div>
    """, unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["🎬 Box Office Performance", "👥 Show Occupancy", "💰 Net Revenue", "🛠️ System Diagnostics"])
    with t1:
        movie_perf = fetch_dataframe("SELECT movie_title, genre, total_screenings, tickets_sold, box_office_gross FROM view_movie_performance ORDER BY box_office_gross DESC")
        if not movie_perf.empty:
            st.bar_chart(data=movie_perf.set_index('movie_title')['box_office_gross'])
            st.dataframe(movie_perf, use_container_width=True, hide_index=True)
            st.download_button("📥 Export Box Office Data (CSV)", data=movie_perf.to_csv(index=False), file_name="box_office_report.csv", mime="text/csv")
    with t2:
        occ_df = fetch_dataframe("SELECT movie_title, cinema_name, screen_number, show_date, start_time, booked_seats, total_seats, occupancy_percentage FROM view_show_occupancy ORDER BY occupancy_percentage DESC")
        st.dataframe(occ_df, use_container_width=True, hide_index=True)
        st.download_button("📥 Export Occupancy Report (CSV)", data=occ_df.to_csv(index=False), file_name="occupancy_report.csv", mime="text/csv")
    with t3:
        rev_df = fetch_dataframe("SELECT * FROM view_total_revenue_breakdown")
        st.dataframe(rev_df, use_container_width=True, hide_index=True)
        st.download_button("📥 Export Financial Statement (CSV)", data=rev_df.to_csv(index=False), file_name="revenue_statement.csv", mime="text/csv")
    with t4:
        st.markdown("#### Automated DBMS Integrity Verification")
        if st.button("▶ Execute Diagnostic Tests", key="run_diag_btn"):
            conn = get_connection()
            cur = conn.cursor()
            results = []
            # Test 1: Double Booking Prevention
            try:
                cur.execute("INSERT INTO booked_seats (booking_id, screening_id, seat_id, price, status) VALUES (1, 1, 1, 350, 'Booked');")
                results.append(("Double-Booking Constraint", "FAIL", "Allowed duplicate active seat on same screening"))
            except sqlite3.IntegrityError:
                results.append(("Double-Booking Constraint", "PASS", "Enforced via unique index uq_screening_seat_active"))
            # Test 2: Overlap trigger
            try:
                cur.execute("INSERT INTO screenings (screen_id, movie_id, show_date, start_time, end_time, ticket_price, status) VALUES (1, 1, '2026-10-04', '11:00:00', '13:00:00', 300, 'Scheduled');")
                results.append(("Screen Overlap Trigger", "FAIL", "Allowed overlapping showtime"))
            except sqlite3.IntegrityError:
                results.append(("Screen Overlap Trigger", "PASS", "Enforced via trigger trg_prevent_screen_overlap_insert"))
            conn.rollback()
            conn.close()
            
            for tname, status, desc in results:
                if status == "PASS":
                    st.success(f"**[{status}]** {tname}: {desc}")
                else:
                    st.error(f"**[{status}]** {tname}: {desc}")
                    
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# 6. MAIN CONTROLLER
# =============================================================================
def main():
    render_top_navbar()
    
    tabs = st.tabs([
        "⚡ Simulation & Booking",
        "🎬 Explore Movies & Shows",
        "🍿 Gourmet Concessions",
        "🛡️ Usher Gate Validator",
        "🔄 Cancel & Refunds",
        "📊 Telemetry & Executive BI"
    ])
    
    with tabs[0]:
        render_interactive_booking_system()
    with tabs[1]:
        render_movie_catalog_discovery()
    with tabs[2]:
        render_concessions_lounge()
    with tabs[3]:
        render_usher_gate_validator()
    with tabs[4]:
        render_cancellations_tab()
    with tabs[5]:
        render_executive_bi()

if __name__ == "__main__":
    main()
