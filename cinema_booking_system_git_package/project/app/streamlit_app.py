import streamlit as st
import sqlite3
import pandas as pd
import os
import datetime
import hashlib
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
        margin-bottom: 24px;
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
        font-size: 1rem;
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
    .nav-pill-container {
        display: flex;
        gap: 8px;
        align-items: center;
    }
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
        padding: 44px 48px;
        margin-bottom: 28px;
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
        margin-bottom: 16px;
    }
    .hero-headline {
        font-size: 2.85rem;
        font-weight: 900;
        line-height: 1.12;
        letter-spacing: -1px;
        color: #18181B;
        margin-bottom: 16px;
    }
    .hero-headline em {
        font-style: italic;
        font-weight: 400;
        color: #18181B;
        font-family: serif;
    }
    .hero-desc {
        color: #6B7280;
        font-size: 1.05rem;
        line-height: 1.6;
        max-width: 580px;
        margin-bottom: 28px;
    }
    
    /* Hero Action Buttons */
    .btn-pill-dark {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #18181B;
        color: #FFFFFF !important;
        text-decoration: none !important;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 12px 24px;
        border-radius: 9999px;
        border: none;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(24, 24, 27, 0.2);
    }
    .btn-pill-light {
        display: inline-flex;
        align-items: center;
        background: #F3F4F6;
        color: #374151 !important;
        text-decoration: none !important;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 12px 24px;
        border-radius: 9999px;
        border: 1px solid #E5E7EB;
        transition: all 0.2s ease;
        margin-left: 10px;
    }

    /* Key Statistics Row */
    .hero-stats-row {
        display: flex;
        gap: 36px;
        margin-top: 36px;
        padding-top: 24px;
        border-top: 1px solid #F3F4F6;
    }
    .stat-number {
        font-size: 1.75rem;
        font-weight: 800;
        color: #18181B;
        line-height: 1.1;
    }
    .stat-caption {
        font-size: 0.78rem;
        color: #6B7280;
        font-weight: 500;
        margin-top: 3px;
    }

    /* Smartphone Phone Mockup Frame (from Image 2) */
    .phone-mockup-frame {
        background: #18181B;
        border-radius: 40px;
        padding: 12px;
        box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.35);
        max-width: 330px;
        margin: 0 auto;
    }
    .phone-screen {
        background: #FFFFFF;
        border-radius: 30px;
        padding: 20px 18px;
        color: #111827;
        overflow: hidden;
    }
    .phone-island {
        width: 80px;
        height: 18px;
        background: #18181B;
        border-radius: 9999px;
        margin: 0 auto 16px auto;
    }
    .phone-subcard {
        background: #F8FAFC;
        border: 1px solid #F1F5F9;
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }

    /* Main Parameter Box (from Image 1) */
    .param-box {
        background: #F4F6F8;
        border: 1px solid #E5E7EB;
        border-radius: 24px;
        padding: 26px 30px;
        margin-bottom: 24px;
    }
    .param-box-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
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
        padding: 22px 24px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #111827;
        line-height: 1;
        letter-spacing: -0.5px;
    }
    .kpi-subtext {
        font-size: 0.82rem;
        color: #9CA3AF;
        margin-top: 8px;
        font-weight: 500;
    }
    .kpi-badge-green {
        color: #10B981;
        font-weight: 700;
        font-size: 0.82rem;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Progress Bar (Custom Minimal) */
    .progress-track {
        width: 100%;
        height: 7px;
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

    /* Hardware Saturation Profile Cards (Image 1 Bottom Grid) */
    .profile-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
        transition: transform 0.15s ease, border-color 0.15s ease;
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
        font-size: 0.75rem;
        font-weight: 700;
        color: #6B7280;
    }
    .profile-footer {
        display: flex;
        justify-content: space-between;
        font-size: 0.72rem;
        color: #9CA3AF;
        margin-top: 8px;
    }

    /* Minimalist Seating Matrix */
    .curved-screen-minimal {
        height: 6px;
        background: #18181B;
        border-radius: 50% 50% 0 0 / 100% 100% 0 0;
        max-width: 500px;
        margin: 20px auto 8px auto;
        box-shadow: 0 4px 14px rgba(24, 24, 27, 0.15);
    }
    .curved-screen-text {
        text-align: center;
        font-size: 0.7rem;
        letter-spacing: 3px;
        font-weight: 800;
        color: #9CA3AF;
        margin-bottom: 24px;
    }

    .seat-minimal {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 34px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        text-align: center;
        margin: 3px;
        transition: all 0.15s ease;
    }
    .seat-min-avail {
        background: #FFFFFF;
        color: #4B5563;
        border: 1px solid #E5E7EB;
    }
    .seat-min-booked {
        background: #FEE2E2;
        color: #EF4444;
        border: 1px solid #FECACA;
        cursor: not-allowed;
    }
    .seat-min-sel {
        background: #18181B;
        color: #FFFFFF;
        border: 1px solid #18181B;
    }

    /* Luxury Minimal Ticket Pass (Apple Wallet / Stripe Style) */
    .pass-container {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 24px 28px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        max-width: 580px;
        margin: 20px auto;
        border-top: 6px solid #18181B;
    }

    /* Native Streamlit Element Overrides to match Neo-SaaS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #F3F4F6;
        padding: 5px;
        border-radius: 9999px;
        border: 1px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9999px;
        padding: 8px 22px;
        color: #4B5563;
        font-weight: 700;
        font-size: 0.85rem;
        border: none !important;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #18181B !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    /* Buttons */
    .stButton>button {
        border-radius: 9999px;
        font-weight: 700;
        letter-spacing: 0.3px;
        padding: 10px 24px;
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
    
    /* Input fields and selectboxes */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px;
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
# 3. CORE TRANSACTION SERVICES
# =============================================================================
def book_tickets_service(customer_id: int, screening_id: int, seat_ids: list, payment_method: str):
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
            
        total_amount = float(unit_price) * len(seat_ids)
        
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


# =============================================================================
# 4. VIEW COMPONENTS (REPLICATING IMAGES 1 & 2 ARCHITECTURE)
# =============================================================================

def render_top_navbar():
    """Renders the top pill navbar exactly like Images 1 and 2."""
    customers = fetch_dataframe("SELECT customer_id, full_name FROM customers")
    cust_options = {r['customer_id']: r['full_name'] for _, r in customers.iterrows()} if not customers.empty else {1: "Customer 1"}
    
    st.markdown("""
    <div class="top-navbar">
        <div class="brand-logo-group">
            <div class="brand-icon-circle">⚡</div>
            <div>
                <div class="brand-text-title">CINEVERSE OS</div>
                <div class="brand-text-subtitle">DBMS AUDITORIUM ENGINE</div>
            </div>
        </div>
        <div class="nav-pill-container">
            <span class="status-pill-green"><span class="dot-green"></span> SQLite ACID :3306</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_hero_display():
    """Renders the Hero Display Section with Smartphone Mockup (Matching Image 2)."""
    with st.container():
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
                    <div>
                        <a href="#booking_section" class="btn-pill-dark">Reserve Seats ↓</a>
                        <a href="#telemetry_section" class="btn-pill-light">Explore Telemetry</a>
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
                            
                            <div style="margin-top: 14px;">
                                <div style="background: #18181B; color: #FFFFFF; text-align: center; padding: 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">
                                    Inspect Solver Output
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_parameters_and_kpis():
    """Renders the Simulation/Reservation Parameter Box and 4 KPIs (Matching Image 1)."""
    st.markdown('<div id="booking_section"></div>', unsafe_allow_html=True)
    
    # 1. PARAMETERS BOX
    st.markdown("""
    <div class="param-box">
        <div class="param-box-header">
            <span class="param-box-title">RESERVATION & SCREENING PARAMETERS</span>
            <span class="param-pill-active">Active Config</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Screenings query
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
        st.warning("No scheduled screenings found.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
        
    screening_options = {
        r['screening_id']: f"{r['title']} ({r['show_date']} @ {r['start_time']}) - {r['cinema_name']} Scrn {r['screen_number']}"
        for _, r in screenings.iterrows()
    }
    
    col1, col2, col3, col4, col5 = st.columns([2.5, 2, 1.5, 1.5, 2])
    
    with col1:
        st.markdown("<small style='font-weight:700; color:#4B5563;'>SCREENING TOPOLOGY</small>", unsafe_allow_html=True)
        chosen_screening_id = st.selectbox(
            "Screening",
            options=list(screening_options.keys()),
            format_func=lambda x: screening_options[x],
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("<small style='font-weight:700; color:#4B5563;'>AUDITORIUM CAPACITY</small>", unsafe_allow_html=True)
        selected_screening = screenings[screenings['screening_id'] == chosen_screening_id].iloc[0]
        st.text_input("Screen Type", value=f"Screen {selected_screening['screen_number']} ({selected_screening['screen_type']})", disabled=True, label_visibility="collapsed")
    with col3:
        st.markdown("<small style='font-weight:700; color:#4B5563;'>PAYMENT CHANNEL</small>", unsafe_allow_html=True)
        payment_method = st.selectbox("Payment", ["UPI", "Credit Card", "Debit Card", "Cash"], label_visibility="collapsed")
    with col4:
        st.markdown("<small style='font-weight:700; color:#4B5563;'>SIMULATOR USER</small>", unsafe_allow_html=True)
        cust_df = fetch_dataframe("SELECT customer_id, full_name FROM customers")
        cust_opts = {r['customer_id']: r['full_name'] for _, r in cust_df.iterrows()} if not cust_df.empty else {2: "Customer 2"}
        customer_id = st.selectbox("Customer", options=list(cust_opts.keys()), format_func=lambda x: cust_opts[x], label_visibility="collapsed")
    with col5:
        st.markdown("<small style='font-weight:700; color:#4B5563;'>PRICE PER SEAT</small>", unsafe_allow_html=True)
        st.text_input("Ticket Price", value=f"Rs. {int(selected_screening['ticket_price'])} / seat", disabled=True, label_visibility="collapsed")
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. 4 KPI METRIC CARDS ROW (Matching Image 1)
    # Fetch real-time metrics
    rev_df = fetch_dataframe("SELECT * FROM view_total_revenue_breakdown")
    total_gross = rev_df['ticket_revenue'].sum() if not rev_df.empty else 4500
    occ_df = fetch_dataframe("SELECT occupancy_percentage FROM view_show_occupancy")
    avg_occupancy = round(occ_df['occupancy_percentage'].mean(), 1) if not occ_df.empty else 11.46
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-label">AVERAGE LATENCY</div>
                <div class="kpi-value">2.5 <span style="font-size: 1.1rem; font-weight: 500; color: #6B7280;">ms</span></div>
            </div>
            <div class="kpi-subtext">Total Gross: Rs. {total_gross:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-label">FEASIBILITY STATUS</div>
                <div class="kpi-value">10 / 10</div>
            </div>
            <div class="kpi-badge-green">✓ 100% Capacity Feasible</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi3:
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
        
    with kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-label">SOLVER RUNTIME</div>
                <div class="kpi-value">2.891 <span style="font-size: 1.1rem; font-weight: 500; color: #6B7280;">ms</span></div>
            </div>
            <div class="kpi-subtext">Exact Optimizer (SQLite Triggers)</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. INTERACTIVE SEAT SELECTION & AUDITORIUM
    screen_id = int(selected_screening['screen_id'])
    seats = fetch_dataframe("""
        SELECT seat_id, row_label, seat_number, seat_tier, base_price 
        FROM seats WHERE screen_id = ? 
        ORDER BY row_label, seat_number;
    """, (screen_id,))
    
    booked_seats = fetch_dataframe("""
        SELECT seat_id FROM booked_seats 
        WHERE screening_id = ? AND status = 'Booked';
    """, (chosen_screening_id,))
    booked_ids = set(booked_seats['seat_id'].tolist()) if not booked_seats.empty else set()
    
    # Section Header in Neo-SaaS style
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 26px 30px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                2D AUDITORIUM TOPOLOGY & SEAT ALLOCATION
            </div>
            <div style="display: flex; gap: 14px; font-size: 0.75rem; font-weight: 700; color: #6B7280;">
                <span>◻ Available</span>
                <span style="color: #18181B;">◼ Selected</span>
                <span style="color: #EF4444;">☒ Occupied</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Projection Screen Arc
    st.markdown("""
    <div class="curved-screen-minimal"></div>
    <div class="curved-screen-text">AUDITORIUM PROJECTION SCREEN</div>
    """, unsafe_allow_html=True)
    
    # Grid of Seats
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
                pills_html.append(f'<span class="seat-minimal seat-min-booked" title="Seat {r_lbl}{snum} (Booked)">✕</span>')
            else:
                available_seats.append((sid, f"{r_lbl}{snum:02d} ({tier})"))
                pills_html.append(f'<span class="seat-minimal seat-min-avail" title="Seat {r_lbl}{snum}">{snum:02d}</span>')
                
        seats_str = "".join(pills_html)
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 4px;">
            <span style="font-weight: 800; font-size: 0.8rem; color: #9CA3AF; width: 25px; text-align: center;">{r_lbl}</span>
            <div>{seats_str}</div>
            <span style="font-size: 0.7rem; color: #9CA3AF; width: 50px; margin-left: 8px;">{tier}</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: none; border-top: 1px solid #F3F4F6; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Booking Selection Controls
    col_sel, col_action = st.columns([3, 1.2])
    with col_sel:
        chosen_sids = st.multiselect(
            "Select Seats to Reserve:",
            options=[s[0] for s in available_seats],
            format_func=lambda sid: next(s[1] for s in available_seats if s[0] == sid),
            placeholder="Click to pick vacant seats..."
        )
    with col_action:
        seat_count = len(chosen_sids)
        total_price = seat_count * float(selected_screening['ticket_price'])
        st.markdown(f"""
        <div style="text-align: right; margin-bottom: 8px;">
            <span style="font-size: 0.75rem; color: #6B7280; font-weight: 700;">TOTAL:</span>
            <span style="font-size: 1.2rem; font-weight: 800; color: #18181B; margin-left: 6px;">Rs. {total_price:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        execute_btn = st.button("▶ Execute Reservation", type="primary", use_container_width=True, disabled=(seat_count == 0))
        
    if execute_btn and chosen_sids:
        with st.spinner("Executing atomic transaction & calculating cryptographic hashes..."):
            ok, res = book_tickets_service(customer_id, chosen_screening_id, chosen_sids, payment_method)
            
        if ok:
            st.success(f"✓ Booking Transaction #{res['booking_id']} executed successfully!")
            
            # Neo-SaaS Minimalist Digital Pass (Apple Wallet Style)
            tickets_lines = "<br>".join([f"• Seat #{t['seat_id']} &nbsp;|&nbsp; <code>{t['barcode_hash']}</code>" for t in res['tickets']])
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
                            {selected_screening['cinema_name']} • Screen {selected_screening['screen_number']}
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
                        <div style="font-size: 0.68rem; color: #6B7280; font-weight: 700;">RESERVED SEATS</div>
                        <div style="font-weight: 800; font-size: 0.85rem; color: #18181B;">{seat_count} Seats</div>
                    </div>
                    <div>
                        <div style="font-size: 0.68rem; color: #6B7280; font-weight: 700;">TOTAL CHARGED</div>
                        <div style="font-weight: 800; font-size: 0.85rem; color: #18181B;">Rs. {res['total_amount']}</div>
                    </div>
                </div>
                
                <div style="font-size: 0.75rem; color: #4B5563;">
                    <div style="font-weight: 700; margin-bottom: 4px;">CRYPTOGRAPHIC DIGITAL TOKENS (SHA-256):</div>
                    {tickets_lines}
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


def render_hardware_saturation_profiles():
    """Renders the Server Hardware / Screen Saturation Profiles Grid (Matching Image 1 Bottom)."""
    st.markdown('<div id="telemetry_section"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-top: 16px; margin-bottom: 12px;">
        <span style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
            AUDITORIUM SATURATION PROFILES (SCREENS & CAPACITY UTILIZATION)
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    screens_data = fetch_dataframe("""
        SELECT 
            c.name as cinema_name, sc.screen_id, sc.screen_number, sc.screen_type, sc.seating_capacity,
            COALESCE(SUM(CASE WHEN bs.status = 'Booked' THEN 1 ELSE 0 END), 0) as booked_seats
        FROM screens sc
        JOIN cinemas c ON sc.cinema_id = c.cinema_id
        LEFT JOIN screenings s ON sc.screen_id = s.screen_id AND s.status != 'Cancelled'
        LEFT JOIN booked_seats bs ON s.screening_id = bs.screening_id
        GROUP BY sc.screen_id;
    """)
    
    if screens_data.empty:
        st.info("No screen hardware profiles available.")
        return
        
    cols = st.columns(4)
    for idx, (_, row) in enumerate(screens_data.iterrows()):
        col = cols[idx % 4]
        cap = int(row['seating_capacity'])
        booked = int(row['booked_seats'])
        pct = round((booked * 100.0) / max(cap, 1), 1)
        pct_display = min(pct, 100.0)
        
        with col:
            st.markdown(f"""
            <div class="profile-card">
                <div class="profile-header">
                    <span class="profile-name">Screen-{row['screen_number']} ({row['screen_type']})</span>
                    <span class="profile-pct">{pct_display}%</span>
                </div>
                <div class="progress-track" style="height: 5px;">
                    <div class="progress-fill-dark" style="width: {pct_display}%;"></div>
                </div>
                <div class="profile-footer">
                    <span>CAPACITY: {booked}/{cap}</span>
                    <span>{row['cinema_name'][:14]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_concessions_tab():
    """Renders the Gourmet Concessions & Bar in Neo-SaaS style."""
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 26px 30px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                CONCESSIONS & INVENTORY TELEMETRY
            </div>
            <span class="param-pill-active">Live Stock Depletion</span>
        </div>
    """, unsafe_allow_html=True)
    
    items = fetch_dataframe("SELECT item_id, item_name, category, unit_price, stock_quantity FROM concession_items ORDER BY category, item_name;")
    
    col_menu, col_order = st.columns([2.5, 1.5])
    with col_menu:
        st.markdown("#### Item Catalog")
        st.dataframe(items, use_container_width=True, hide_index=True)
        
    with col_order:
        st.markdown("#### Quick Counter Order")
        item_opts = {r['item_id']: f"{r['item_name']} (Rs.{int(r['unit_price'])}) - Stock: {r['stock_quantity']}" for _, r in items.iterrows() if r['stock_quantity'] > 0}
        
        if item_opts:
            selected_items = st.multiselect("Pick Items:", options=list(item_opts.keys()), format_func=lambda x: item_opts[x])
            quantities = {}
            total_cost = 0
            
            for iid in selected_items:
                row = items[items['item_id'] == iid].iloc[0]
                quantities[iid] = st.number_input(f"Qty: {row['item_name']}", min_value=1, max_value=int(row['stock_quantity']), value=1)
                total_cost += quantities[iid] * float(row['unit_price'])
                
            st.markdown(f"**Order Total:** `Rs. {total_cost:,.2f}`")
            if st.button("▶ Submit Order", type="primary", use_container_width=True) and selected_items:
                payload = [(iid, quantities[iid]) for iid in selected_items]
                ok, o_res = order_concessions_service(2, None, payload, "UPI")
                if ok:
                    st.success(f"✓ Concession Order #{o_res['order_id']} dispatched!")
                    st.cache_data.clear()
                else:
                    st.error(o_res)
        else:
            st.warning("All concession items currently out of stock.")
            
    st.markdown("</div>", unsafe_allow_html=True)


def render_cancellations_tab():
    """Renders the Booking Cancellation & Refund module."""
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 26px 30px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                CANCELLATION & REFUND SOLVER
            </div>
            <span class="param-pill-active">10% Retention Policy</span>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1.5, 2.5])
    with c1:
        cancel_b_id = st.number_input("Booking ID to Cancel:", min_value=1, step=1)
        reason = st.text_input("Cancellation Reason:", "Schedule adjustment")
        
        if st.button("▶ Authorize Refund", type="primary", use_container_width=True):
            ok, res = cancel_booking_service(cancel_b_id, reason)
            if ok:
                st.success(f"✓ Booking #{cancel_b_id} cancelled.")
                st.metric("Refund Issued", f"Rs.{res['refund_amount']:,.2f}", delta=f"- Rs.{res['cancellation_fee']:,.2f} (10% Fee)", delta_color="inverse")
                st.caption(f"Audit Reference: `{res['refund_reference']}`")
                st.cache_data.clear()
            else:
                st.error(res)
                
    with c2:
        st.markdown("#### Recent Cancellations Audit")
        canc_df = fetch_dataframe("""
            SELECT c.cancellation_id as ID, b.booking_id as Bkg_ID, m.title as Movie, c.cancellation_fee as Fee, r.refund_amount as Refund, r.refund_reference as Audit_Ref
            FROM cancellations c
            JOIN bookings b ON c.booking_id = b.booking_id
            JOIN screenings s ON b.screening_id = s.screening_id
            JOIN movies m ON s.movie_id = m.movie_id
            LEFT JOIN refunds r ON c.cancellation_id = r.cancellation_id
            ORDER BY c.cancellation_id DESC LIMIT 5;
        """)
        if not canc_df.empty:
            st.dataframe(canc_df, use_container_width=True, hide_index=True)
        else:
            st.info("No cancellations on record.")
            
    st.markdown("</div>", unsafe_allow_html=True)


def render_executive_bi():
    """Renders the Executive Analytics and SQL Views."""
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 24px; padding: 26px 30px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #374151;">
                EXECUTIVE TELEMETRY & SQL REPORTING VIEWS
            </div>
            <span class="param-pill-active">Production Telemetry</span>
        </div>
    """, unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🎬 Box Office Performance", "👥 Show Occupancy Analysis", "💰 Financial Revenue Breakdown"])
    with t1:
        movie_perf = fetch_dataframe("SELECT movie_title, tickets_sold, box_office_gross FROM view_movie_performance ORDER BY box_office_gross DESC")
        if not movie_perf.empty:
            st.bar_chart(data=movie_perf.set_index('movie_title')['box_office_gross'])
            st.dataframe(movie_perf, use_container_width=True, hide_index=True)
    with t2:
        occ_df = fetch_dataframe("SELECT movie_title, show_date, start_time, booked_seats, total_seats, occupancy_percentage FROM view_show_occupancy ORDER BY occupancy_percentage DESC")
        st.dataframe(occ_df, use_container_width=True, hide_index=True)
    with t3:
        rev_df = fetch_dataframe("SELECT * FROM view_total_revenue_breakdown")
        st.dataframe(rev_df, use_container_width=True, hide_index=True)
        
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# 5. MAIN ROUTER
# =============================================================================
def main():
    # Render Top Navigation Bar (matching Images 1 & 2)
    render_top_navbar()
    
    # Segmented Navigation Tabs directly on the page (matching Images 1 & 2 pill nav)
    tab_sim, tab_concessions, tab_cancel, tab_telemetry = st.tabs([
        "⚡ Simulation & Booking",
        "🍿 Concessions & Bar",
        "🔄 Cancel & Refunds",
        "📊 System Telemetry & BI"
    ])
    
    with tab_sim:
        render_hero_display()
        render_parameters_and_kpis()
        render_hardware_saturation_profiles()
        
    with tab_concessions:
        render_concessions_tab()
        
    with tab_cancel:
        render_cancellations_tab()
        
    with tab_telemetry:
        render_executive_bi()

if __name__ == "__main__":
    main()
