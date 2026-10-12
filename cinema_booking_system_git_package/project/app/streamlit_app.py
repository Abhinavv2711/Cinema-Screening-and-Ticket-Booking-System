import streamlit as st
import sqlite3
import pandas as pd
import os
import datetime
import hashlib
import json

# =============================================================================
# 1. PAGE CONFIGURATION & CINEMATIC THEME (ULTRA-PREMIUM UI/UX)
# =============================================================================
st.set_page_config(
    page_title="CINEVERSE LUXE | Cinema Screening & Ticketing",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Cinematic CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Cinzel:wght@600;700;800;900&display=swap');

    /* Global Typography & Base */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Background adjustments */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #121826 0%, #080b11 60%, #040608 100%);
        color: #f1f5f9;
    }

    /* Premium Header Banner */
    .brand-hero {
        background: linear-gradient(135deg, rgba(235, 16, 37, 0.15) 0%, rgba(245, 197, 24, 0.08) 50%, rgba(18, 24, 38, 0.8) 100%);
        border: 1px solid rgba(255, 215, 0, 0.18);
        border-radius: 20px;
        padding: 28px 36px;
        margin-bottom: 25px;
        box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.7), inset 0 1px 1px rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(14px);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-title {
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 3px;
        background: linear-gradient(135deg, #FFF6D6 0%, #E6C665 40%, #E50914 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        text-transform: uppercase;
    }
    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 500;
        letter-spacing: 1px;
        margin-top: 6px;
    }
    .brand-badge {
        background: rgba(229, 9, 20, 0.18);
        color: #ff4d4d;
        border: 1px solid rgba(229, 9, 20, 0.4);
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(18, 24, 38, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
        transition: transform 0.25s ease, border-color 0.25s ease;
    }
    .glass-card:hover {
        border-color: rgba(245, 197, 24, 0.35);
        transform: translateY(-2px);
    }

    /* Movie Poster Cards */
    .movie-card {
        background: linear-gradient(180deg, rgba(26, 34, 52, 0.7) 0%, rgba(14, 19, 30, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .movie-card:hover {
        transform: translateY(-5px);
        border-color: #f5c518;
        box-shadow: 0 20px 40px rgba(245, 197, 24, 0.15);
    }
    .movie-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-right: 6px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .badge-imax { background: rgba(0, 168, 255, 0.18); color: #00a8ff; border: 1px solid rgba(0, 168, 255, 0.4); }
    .badge-rating { background: rgba(255, 255, 255, 0.1); color: #cbd5e1; border: 1px solid rgba(255, 255, 255, 0.2); }
    .badge-genre { background: rgba(245, 197, 24, 0.15); color: #f5c518; border: 1px solid rgba(245, 197, 24, 0.3); }

    /* Curved Auditorium Projection Screen */
    .curved-screen-container {
        text-align: center;
        margin: 30px auto 40px auto;
        max-width: 650px;
        position: relative;
    }
    .curved-screen {
        height: 14px;
        background: linear-gradient(180deg, #38bdf8 0%, rgba(56, 189, 248, 0.05) 100%);
        border-radius: 50% 50% 0 0 / 100% 100% 0 0;
        box-shadow: 0 -4px 28px #38bdf8, 0 12px 30px rgba(56, 189, 248, 0.35);
        margin-bottom: 12px;
    }
    .screen-label {
        font-size: 0.75rem;
        letter-spacing: 5px;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 700;
    }

    /* Seating Matrix Layout */
    .seat-row {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;
        gap: 8px;
    }
    .row-tag {
        font-weight: 700;
        color: #64748b;
        width: 28px;
        font-size: 0.85rem;
        text-align: center;
    }
    .seat-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 34px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        text-align: center;
        transition: all 0.15s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .seat-avail {
        background: rgba(30, 41, 59, 0.9);
        color: #94a3b8;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    .seat-avail:hover {
        background: #f5c518;
        color: #0b0e14;
        border-color: #f5c518;
        transform: scale(1.1);
        cursor: pointer;
    }
    .seat-booked {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        cursor: not-allowed;
        opacity: 0.6;
    }
    .seat-selected {
        background: linear-gradient(135deg, #f5c518 0%, #eab308 100%);
        color: #090d16;
        border: 1px solid #fef08a;
        box-shadow: 0 0 16px rgba(245, 197, 24, 0.6);
        transform: scale(1.08);
    }

    /* Seat Tier Legend */
    .legend-item {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin: 0 12px;
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 600;
    }
    .legend-box {
        width: 14px;
        height: 14px;
        border-radius: 4px;
    }

    /* Luxury Ticket Pass */
    .ticket-pass {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(245, 197, 24, 0.3);
        border-radius: 20px;
        padding: 26px;
        position: relative;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
        color: #f8fafc;
        max-width: 680px;
        margin: 20px auto;
        overflow: hidden;
    }
    .ticket-pass::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 5px;
        background: linear-gradient(90deg, #E50914, #F5C518, #00A8FF);
    }
    .ticket-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 1px dashed rgba(255, 255, 255, 0.15);
        padding-bottom: 18px;
        margin-bottom: 18px;
    }
    .ticket-barcode {
        font-family: 'Courier New', monospace;
        letter-spacing: 6px;
        background: #020617;
        padding: 12px 18px;
        border-radius: 8px;
        text-align: center;
        font-size: 0.85rem;
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.2);
        margin-top: 15px;
    }

    /* Metric Cards */
    .metric-hero {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-lbl {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-top: 4px;
        font-weight: 600;
    }

    /* Streamlit Tab & Button Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e50914 0%, #b91c1c 100%) !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(229, 9, 20, 0.4);
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #e50914 0%, #dc2626 100%);
        border: none;
        box-shadow: 0 4px 18px rgba(229, 9, 20, 0.4);
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(229, 9, 20, 0.6);
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 2. DATABASE UTILITIES & PERFORMANCE LAYER
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
    """High-performance cached query executor for analytical reads."""
    try:
        with get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.error(f"⚠️ Query Execution Error: {e}")
        return pd.DataFrame()


# =============================================================================
# 3. MOVIE METADATA & POSTER GALLERY ASSETS
# =============================================================================
# High-resolution themed poster backdrops
MOVIE_POSTERS = {
    "Oppenheimer": {
        "poster": "https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=800&auto=format&fit=crop",
        "tagline": "The world forever changes.",
        "rating_score": "⭐ 8.9/10",
        "director": "Christopher Nolan"
    },
    "Dune: Part Two": {
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=800&auto=format&fit=crop",
        "tagline": "Long live the fighters.",
        "rating_score": "⭐ 8.8/10",
        "director": "Denis Villeneuve"
    },
    "Interstellar": {
        "poster": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=800&auto=format&fit=crop",
        "tagline": "Mankind was born on Earth. It was never meant to die here.",
        "rating_score": "⭐ 8.7/10",
        "director": "Christopher Nolan"
    },
    "Kalki 2898 AD": {
        "poster": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=800&auto=format&fit=crop",
        "tagline": "The future of Indian cinematic mythology.",
        "rating_score": "⭐ 8.4/10",
        "director": "Nag Ashwin"
    },
    "Inception": {
        "poster": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?q=80&w=800&auto=format&fit=crop",
        "tagline": "Your mind is the scene of the crime.",
        "rating_score": "⭐ 8.8/10",
        "director": "Christopher Nolan"
    }
}

CONCESSION_ICONS = {
    "Popcorn": "🍿",
    "Beverage": "🥤",
    "Snack": "🥨",
    "Combo": "🍱"
}


# =============================================================================
# 4. BUSINESS LOGIC & TRANSACTION SERVICES
# =============================================================================
def book_tickets_service(customer_id: int, screening_id: int, seat_ids: list, payment_method: str):
    """Executes atomic multi-seat booking with SHA-256 digital barcode issuance."""
    if not seat_ids:
        return False, "Please select at least one seat to proceed."
        
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN TRANSACTION;")
        
        # Check screening validity & get unit price
        cur.execute("SELECT ticket_price, movie_id, screen_id FROM screenings WHERE screening_id = ?", (screening_id,))
        show_row = cur.fetchone()
        if not show_row:
            raise ValueError("Designated screening not found.")
        unit_price = show_row[0]
        
        # Verify seats are still vacant (concurrency safety)
        placeholders = ','.join(['?'] * len(seat_ids))
        cur.execute(f"""
            SELECT seat_id FROM booked_seats 
            WHERE screening_id = ? AND seat_id IN ({placeholders}) AND status = 'Booked'
        """, [screening_id] + seat_ids)
        clashes = cur.fetchall()
        if clashes:
            raise ValueError(f"Seat ID(s) {[c[0] for c in clashes]} were just reserved by another guest. Please pick alternate seats.")
            
        total_amount = float(unit_price) * len(seat_ids)
        
        # Insert master booking
        cur.execute("""
            INSERT INTO bookings (customer_id, screening_id, total_amount, booking_status)
            VALUES (?, ?, ?, 'Confirmed')
        """, (customer_id, screening_id, total_amount))
        booking_id = cur.lastrowid
        
        # Insert individual seats & cryptographically signed digital tickets
        tickets_issued = []
        for sid in seat_ids:
            cur.execute("""
                INSERT INTO booked_seats (booking_id, screening_id, seat_id, price, status)
                VALUES (?, ?, ?, ?, 'Booked')
            """, (booking_id, screening_id, sid, unit_price))
            booked_seat_id = cur.lastrowid
            
            # SHA-256 digital barcode
            tkt_num = f"LUXE-B{booking_id}-S{sid}-{datetime.datetime.now().strftime('%y%m%d%H%M')}"
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
            
        # Record payment transaction
        txn_ref = f"TXN-LUXE-{payment_method[:3].upper()}-{booking_id}-{datetime.datetime.now().strftime('%H%M%S')}"
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
            
        txn_ref = f"TXN-FNB-{order_id}-{datetime.datetime.now().strftime('%H%M%S')}"
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
        
        ref_code = f"REF-LUXE-{booking_id}-{datetime.datetime.now().strftime('%H%M%S')}"
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
# 5. UI VIEW IMPLEMENTATIONS
# =============================================================================

def render_hero_header():
    """Renders the top branding and hero header."""
    st.markdown("""
    <div class="brand-hero">
        <div>
            <div class="brand-title">CINEVERSE LUXE</div>
            <div class="brand-subtitle">PREMIER CINEMA SCREENING & RESERVATION SYSTEM</div>
        </div>
        <div style="text-align: right;">
            <span class="brand-badge">⚡ LIVE EXPERIENCE</span>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 6px; font-weight: 600;">
                HYDERABAD • MUMBAI • BANGALORE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_movie_gallery():
    """Renders the visually rich movie showcase and schedule."""
    st.markdown("### 🎬 Now Showing & Showtimes")
    
    # Fetch all scheduled screenings with joined movie & cinema details
    screenings = fetch_dataframe("""
        SELECT 
            s.screening_id, m.movie_id, m.title, m.genre, m.duration_minutes, m.rating, m.language,
            c.name as cinema_name, sc.screen_number, sc.screen_type,
            s.show_date, s.start_time, s.end_time, s.ticket_price
        FROM screenings s
        JOIN screens sc ON s.screen_id = sc.screen_id
        JOIN cinemas c ON sc.cinema_id = c.cinema_id
        JOIN movies m ON s.movie_id = m.movie_id
        WHERE s.status != 'Cancelled'
        ORDER BY s.show_date, s.start_time;
    """)
    
    if screenings.empty:
        st.info("No movie screenings currently scheduled.")
        return
        
    # Group screenings by movie
    unique_movies = screenings[['movie_id', 'title', 'genre', 'duration_minutes', 'rating', 'language']].drop_duplicates()
    
    cols = st.columns(3)
    for idx, (_, mov) in enumerate(unique_movies.iterrows()):
        col = cols[idx % 3]
        meta = MOVIE_POSTERS.get(mov['title'], {
            "poster": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=800&auto=format&fit=crop",
            "tagline": "A cinematic masterpiece.",
            "rating_score": "⭐ 8.5/10",
            "director": "Visionary Director"
        })
        
        mov_shows = screenings[screenings['movie_id'] == mov['movie_id']]
        
        with col:
            with st.container(border=True):
                st.image(meta['poster'], use_container_width=True)
                st.markdown(f"#### {mov['title']}")
                
                # Badges row
                st.markdown(f"""
                <div>
                    <span class="movie-badge badge-genre">{mov['genre']}</span>
                    <span class="movie-badge badge-rating">{mov['rating']}</span>
                    <span class="movie-badge badge-rating">{mov['language']}</span>
                    <span class="movie-badge badge-rating">⏱️ {mov['duration_minutes']}m</span>
                </div>
                <div style="color: #94a3b8; font-size: 0.85rem; font-style: italic; margin-bottom: 12px;">
                    "{meta['tagline']}"
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**Available Showtimes:**")
                for _, show in mov_shows.iterrows():
                    st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.6); padding: 8px 12px; border-radius: 8px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255,255,255,0.05);">
                        <div>
                            <div style="font-weight: 700; color: #f8fafc; font-size: 0.85rem;">{show['start_time']} - {show['end_time']}</div>
                            <div style="font-size: 0.72rem; color: #94a3b8;">{show['cinema_name']} • Scrn {show['screen_number']} ({show['screen_type']})</div>
                        </div>
                        <div style="font-weight: 800; color: #f5c518; font-size: 0.95rem;">
                            Rs.{int(show['ticket_price'])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

def render_interactive_booking():
    """Renders the graphical 2D seat matrix and checkout."""
    st.markdown("### 🎟️ Reserve Your Luxury Experience")
    
    # 1. Screening Selector
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
        st.warning("No screenings available for booking.")
        return
        
    screening_options = {
        r['screening_id']: f"{r['title']} | {r['cinema_name']} (Screen {r['screen_number']} - {r['screen_type']}) | {r['show_date']} @ {r['start_time']} [Rs.{int(r['ticket_price'])}]"
        for _, r in screenings.iterrows()
    }
    
    col_sel, col_pay = st.columns([3, 1])
    with col_sel:
        selected_id = st.selectbox(
            "Select Experience & Showtime:", 
            options=list(screening_options.keys()), 
            format_func=lambda x: screening_options[x],
            help="Select movie, cinema, auditorium type and time."
        )
    with col_pay:
        pay_method = st.selectbox("Preferred Payment Method:", ["UPI", "Credit Card", "Debit Card", "Cash"])
        
    selected_screening = screenings[screenings['screening_id'] == selected_id].iloc[0]
    screen_id = int(selected_screening['screen_id'])
    unit_price = float(selected_screening['ticket_price'])
    
    # 2. Fetch Auditorium Seats & Current Bookings
    seats = fetch_dataframe("""
        SELECT seat_id, row_label, seat_number, seat_tier, base_price 
        FROM seats 
        WHERE screen_id = ? 
        ORDER BY row_label, seat_number;
    """, (screen_id,))
    
    booked_seats = fetch_dataframe("""
        SELECT seat_id FROM booked_seats 
        WHERE screening_id = ? AND status = 'Booked';
    """, (selected_id,))
    booked_ids = set(booked_seats['seat_id'].tolist()) if not booked_seats.empty else set()
    
    # 3. Visual Curved Screen Representation
    st.markdown("""
    <div class="curved-screen-container">
        <div class="curved-screen"></div>
        <div class="screen-label">ALL EYES ON AUDITORIUM CURVED SCREEN</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 4. Interactive Seat Grid using Checkboxes / Multiselect
    # Group seats by row
    rows = sorted(seats['row_label'].unique())
    
    # Render Visual Legend
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <span class="legend-item"><span class="legend-box" style="background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(148, 163, 184, 0.4);"></span> Available</span>
        <span class="legend-item"><span class="legend-box" style="background: #f5c518;"></span> Selected</span>
        <span class="legend-item"><span class="legend-box" style="background: rgba(239, 68, 68, 0.3); border: 1px solid #ef4444;"></span> Occupied</span>
    </div>
    """, unsafe_allow_html=True)
    
    available_seat_options = []
    
    # Layout visual rows
    for r_lbl in rows:
        row_seats = seats[seats['row_label'] == r_lbl].sort_values('seat_number')
        tier = row_seats.iloc[0]['seat_tier']
        
        # Build HTML display row for visual status
        seat_pills_html = []
        for _, s_row in row_seats.iterrows():
            sid = s_row['seat_id']
            snum = s_row['seat_number']
            if sid in booked_ids:
                seat_pills_html.append(f'<span class="seat-pill seat-booked" title="Seat {r_lbl}{snum} (Booked)">✕</span>')
            else:
                available_seat_options.append((sid, f"{r_lbl}{snum:02d} ({tier})"))
                seat_pills_html.append(f'<span class="seat-pill seat-avail" title="Seat {r_lbl}{snum} ({tier})">{snum:02d}</span>')
                
        pills_str = "".join(seat_pills_html)
        st.markdown(f"""
        <div class="seat-row">
            <span class="row-tag">{r_lbl}</span>
            <div style="display: flex; gap: 8px;">{pills_str}</div>
            <span style="font-size: 0.7rem; color: #64748b; margin-left: 10px; width: 60px;">{tier}</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # 5. Multi-seat Picker
    c_pick, c_summary = st.columns([2, 1])
    with c_pick:
        st.markdown("#### Select Seats to Reserve")
        chosen_sids = st.multiselect(
            "Pick Seat Numbers:",
            options=[s[0] for s in available_seat_options],
            format_func=lambda sid: next(s[1] for s in available_seat_options if s[0] == sid),
            help="Choose one or more available seats."
        )
        
    with c_summary:
        st.markdown("#### Booking Summary")
        ticket_count = len(chosen_sids)
        subtotal = unit_price * ticket_count
        convenience_fee = round(subtotal * 0.05, 2) if ticket_count > 0 else 0.0
        grand_total = subtotal + convenience_fee
        
        with st.container(border=True):
            st.markdown(f"**Movie:** {selected_screening['title']}")
            st.markdown(f"**Auditorium:** Screen {selected_screening['screen_number']} ({selected_screening['screen_type']})")
            st.markdown(f"**Seats Selected:** `{ticket_count}`")
            st.markdown(f"**Base Amount:** Rs. {subtotal:,.2f}")
            st.markdown(f"**Convenience Fee (5%):** Rs. {convenience_fee:,.2f}")
            st.markdown(f"### Grand Total: Rs. {grand_total:,.2f}")
            
            confirm_btn = st.button("Proceed to Instant Confirmation 💳", type="primary", use_container_width=True, disabled=(ticket_count == 0))
            
    # Process Transaction
    if confirm_btn and chosen_sids:
        with st.spinner("Locking seats & generating digital boarding pass..."):
            success, res = book_tickets_service(
                customer_id=st.session_state.get("current_customer", 2),
                screening_id=selected_id,
                seat_ids=chosen_sids,
                payment_method=pay_method
            )
            
        if success:
            st.success(f"🎉 Reservation Successful! Booking Reference #{res['booking_id']}")
            st.balloons()
            
            # Render Luxurious Boarding Pass
            seats_str = ", ".join([f"Seat #{t['seat_id']}" for t in res['tickets']])
            hashes_str = "<br>".join([f"Ticket #{t['ticket_number']}: <b>{t['barcode_hash']}</b>" for t in res['tickets']])
            
            st.markdown(f"""
            <div class="ticket-pass">
                <div class="ticket-header">
                    <div>
                        <div style="color: #f5c518; font-size: 0.75rem; letter-spacing: 2px; font-weight: 700; text-transform: uppercase;">
                            LUXURY ADMISSION PASS
                        </div>
                        <div style="font-family: 'Cinzel', serif; font-size: 1.8rem; font-weight: 800; color: #ffffff; margin-top: 4px;">
                            {selected_screening['title']}
                        </div>
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 2px;">
                            {selected_screening['cinema_name']} • Screen {selected_screening['screen_number']} ({selected_screening['screen_type']})
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.75rem; color: #94a3b8;">BOOKING ID</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #38bdf8;">#{res['booking_id']}</div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 18px;">
                    <div>
                        <div style="color: #64748b; font-size: 0.7rem; text-transform: uppercase; font-weight: 700;">DATE</div>
                        <div style="font-weight: 700; font-size: 0.95rem; color: #f8fafc;">{selected_screening['show_date']}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.7rem; text-transform: uppercase; font-weight: 700;">SHOWTIME</div>
                        <div style="font-weight: 700; font-size: 0.95rem; color: #f8fafc;">{selected_screening['start_time']}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.7rem; text-transform: uppercase; font-weight: 700;">CONFIRMED SEATS</div>
                        <div style="font-weight: 700; font-size: 0.95rem; color: #f5c518;">{seats_str}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.7rem; text-transform: uppercase; font-weight: 700;">TOTAL PAID</div>
                        <div style="font-weight: 700; font-size: 0.95rem; color: #38bdf8;">Rs. {res['total_amount']}</div>
                    </div>
                </div>
                
                <div class="ticket-barcode">
                    <div>DIGITAL CRYPTOGRAPHIC TOKENS (SHA-256)</div>
                    <div style="font-size: 0.78rem; margin-top: 6px; color: #94a3b8;">{hashes_str}</div>
                    <div style="margin-top: 8px; font-size: 0.65rem; color: #475569;">TXN REF: {res['transaction_reference']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.cache_data.clear()
        else:
            st.error(f"❌ Booking Transaction Failed: {res}")

def render_concessions_lounge():
    """Renders the Gourmet Concessions & Food Ordering Bar."""
    st.markdown("### 🍿 The Gourmet Lounge & Concessions")
    
    items = fetch_dataframe("""
        SELECT item_id, item_name, category, unit_price, stock_quantity 
        FROM concession_items 
        ORDER BY category, item_name;
    """)
    
    if items.empty:
        st.info("Concessions counter is currently closed.")
        return
        
    tab_order, tab_catalog = st.tabs(["🛒 Order Concessions", "📋 Live Inventory Status"])
    
    with tab_catalog:
        st.dataframe(items, use_container_width=True, hide_index=True)
        
    with tab_order:
        c_left, c_cart = st.columns([2, 1])
        
        with c_left:
            st.markdown("#### Chef's Selection")
            categories = items['category'].unique()
            selected_qtys = {}
            
            for cat in categories:
                cat_icon = CONCESSION_ICONS.get(cat, "🍴")
                st.markdown(f"##### {cat_icon} {cat}")
                cat_items = items[items['category'] == cat]
                
                c_subcols = st.columns(2)
                for i_idx, (_, row) in enumerate(cat_items.iterrows()):
                    with c_subcols[i_idx % 2]:
                        with st.container(border=True):
                            st.markdown(f"**{row['item_name']}**")
                            st.markdown(f"<span style='color: #f5c518; font-weight: 700;'>Rs. {int(row['unit_price'])}</span> • Stock: `{row['stock_quantity']}`", unsafe_allow_html=True)
                            
                            if row['stock_quantity'] > 0:
                                qty = st.number_input(
                                    f"Quantity", 
                                    min_value=0, 
                                    max_value=int(row['stock_quantity']), 
                                    value=0, 
                                    step=1, 
                                    key=f"item_qty_{row['item_id']}"
                                )
                                if qty > 0:
                                    selected_qtys[row['item_id']] = (row['item_name'], row['unit_price'], qty)
                            else:
                                st.caption("❌ Sold Out")
                                
        with c_cart:
            st.markdown("#### 🛍️ Order Tray")
            with st.container(border=True):
                linked_booking = st.number_input("Link to Booking ID (Optional):", min_value=0, value=0, help="Optional booking ID to deliver food straight to auditorium seat.")
                
                if not selected_qtys:
                    st.info("Your tray is empty. Add concessions from the menu.")
                else:
                    running_total = 0.0
                    for iid, (name, price, qty) in selected_qtys.items():
                        line_tot = price * qty
                        running_total += line_tot
                        st.markdown(f"• **{qty}x** {name} <span style='float:right;'>Rs. {line_tot:,.2f}</span>", unsafe_allow_html=True)
                        
                    st.divider()
                    st.markdown(f"### Tray Total: Rs. {running_total:,.2f}")
                    
                    if st.button("Place Gourmet Order 🚀", type="primary", use_container_width=True):
                        cart_payload = [(iid, q) for iid, (_, _, q) in selected_qtys.items()]
                        with st.spinner("Preparing transaction..."):
                            ok, ord_res = order_concessions_service(
                                customer_id=st.session_state.get("current_customer", 2),
                                booking_id=linked_booking,
                                cart_items=cart_payload,
                                payment_method="UPI"
                            )
                        if ok:
                            st.success(f"✅ Order #{ord_res['order_id']} placed successfully! Amount Paid: Rs. {ord_res['total']}")
                            st.cache_data.clear()
                        else:
                            st.error(f"Order failed: {ord_res}")

def render_cancellations():
    """Renders the transparent booking cancellation and automated refund engine."""
    st.markdown("### ❌ Self-Service Booking Cancellation")
    
    st.markdown("""
    <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px;">
        <b style="color: #ef4444;">Cancellation Policy:</b> Cancellations are accepted up to showtime. 
        A transparent <b>10% administrative fee</b> is deducted, and the remaining 90% is instantaneously refunded to the original payment method.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container(border=True):
            cancel_b_id = st.number_input("Enter Booking ID to Cancel:", min_value=1, step=1)
            cancel_reason = st.text_input("Reason for Cancellation:", "Schedule change / Customer request")
            
            if st.button("Authorize Cancellation & Instant Refund ↩️", type="primary", use_container_width=True):
                with st.spinner("Processing automated refund..."):
                    ok, can_res = cancel_booking_service(cancel_b_id, cancel_reason)
                if ok:
                    st.success(f"✅ Booking #{cancel_b_id} successfully cancelled.")
                    st.metric("Refund Disbursed", f"Rs. {can_res['refund_amount']:,.2f}", delta=f"- Rs. {can_res['cancellation_fee']:,.2f} (10% Fee)", delta_color="inverse")
                    st.caption(f"Refund Audit Reference: `{can_res['refund_reference']}`")
                    st.cache_data.clear()
                else:
                    st.error(f"Cancellation Failed: {can_res}")
                    
    with col2:
        st.markdown("#### Audit Trail (Recent Cancellations)")
        cancellations_df = fetch_dataframe("""
            SELECT 
                c.cancellation_id as ID, b.booking_id as Bkg_ID, m.title as Movie, 
                c.cancellation_fee as Fee, r.refund_amount as Refund, r.refund_reference as Ref
            FROM cancellations c
            JOIN bookings b ON c.booking_id = b.booking_id
            JOIN screenings s ON b.screening_id = s.screening_id
            JOIN movies m ON s.movie_id = m.movie_id
            LEFT JOIN refunds r ON c.cancellation_id = r.cancellation_id
            ORDER BY c.cancellation_id DESC LIMIT 5;
        """)
        if not cancellations_df.empty:
            st.dataframe(cancellations_df, use_container_width=True, hide_index=True)
        else:
            st.info("No prior cancellations recorded.")

def render_executive_analytics():
    """Renders the executive dashboard with charts and business intelligence metrics."""
    st.markdown("### 📊 Executive BI & Financial Intelligence")
    
    # 1. High-Level KPI Summary
    rev_df = fetch_dataframe("SELECT * FROM view_total_revenue_breakdown")
    total_tickets = rev_df['ticket_revenue'].sum() if not rev_df.empty else 0
    total_concessions = rev_df['concession_revenue'].sum() if not rev_df.empty else 0
    total_retained_fees = rev_df['cancellation_penalties_retained'].sum() if not rev_df.empty else 0
    net_operating = rev_df['net_operating_revenue'].sum() if not rev_df.empty else 0
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-hero">
            <div class="metric-val">Rs. {total_tickets:,.0f}</div>
            <div class="metric-lbl">Box Office Gross</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-hero">
            <div class="metric-val">Rs. {total_concessions:,.0f}</div>
            <div class="metric-lbl">Concession Sales</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-hero">
            <div class="metric-val">Rs. {total_retained_fees:,.0f}</div>
            <div class="metric-lbl">Cancellation Fees</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-hero">
            <div class="metric-val" style="background: linear-gradient(135deg, #f5c518 0%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Rs. {net_operating:,.0f}
            </div>
            <div class="metric-lbl">Net Operating Rev</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab_box, tab_occ, tab_fnb, tab_full = st.tabs([
        "🎬 Box Office by Movie", 
        "👥 Auditorium Occupancy", 
        "🍿 F&B Performance", 
        "📑 Comprehensive SQL Views"
    ])
    
    with tab_box:
        st.markdown("#### Box Office Performance by Title")
        movie_perf = fetch_dataframe("SELECT movie_title, tickets_sold, box_office_gross FROM view_movie_performance ORDER BY box_office_gross DESC")
        if not movie_perf.empty:
            st.bar_chart(data=movie_perf.set_index('movie_title')['box_office_gross'])
            st.dataframe(movie_perf, use_container_width=True, hide_index=True)
            
    with tab_occ:
        st.markdown("#### Showtime Occupancy Rates (%)")
        occ_df = fetch_dataframe("""
            SELECT movie_title || ' (' || start_time || ')' as show_label, occupancy_percentage, booked_seats, total_seats 
            FROM view_show_occupancy 
            ORDER BY occupancy_percentage DESC
        """)
        if not occ_df.empty:
            st.bar_chart(data=occ_df.set_index('show_label')['occupancy_percentage'])
            st.dataframe(occ_df, use_container_width=True, hide_index=True)
            
    with tab_fnb:
        st.markdown("#### Concessions Revenue Contribution")
        fnb_df = fetch_dataframe("SELECT item_name, total_units_sold, total_revenue FROM view_concession_sales_summary ORDER BY total_revenue DESC")
        if not fnb_df.empty:
            st.bar_chart(data=fnb_df.set_index('item_name')['total_revenue'])
            st.dataframe(fnb_df, use_container_width=True, hide_index=True)
            
    with tab_full:
        st.markdown("#### Cinema Chain Financial Statements")
        st.dataframe(rev_df, use_container_width=True, hide_index=True)


# =============================================================================
# 6. MAIN APPLICATION ENTRY POINT & ROUTER
# =============================================================================
def main():
    # Sidebar Branding & Navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-family: 'Cinzel', serif; font-size: 1.5rem; font-weight: 800; color: #f5c518; letter-spacing: 2px;">
                CINEVERSE
            </div>
            <div style="font-size: 0.72rem; color: #64748b; letter-spacing: 1px;">
                ENTERPRISE CINEMA SUITE
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        menu = {
            "🎬 Now Showing": render_movie_gallery,
            "🎟️ Book Tickets": render_interactive_booking,
            "🍿 Concessions & Bar": render_concessions_lounge,
            "❌ Cancel & Refunds": render_cancellations,
            "📊 Executive Dashboard": render_executive_analytics
        }
        
        choice = st.radio("Navigation", list(menu.keys()), label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("##### 👤 User Profile (Simulator)")
        customers = fetch_dataframe("SELECT customer_id, full_name, email FROM customers")
        if not customers.empty:
            cust_dict = {r['customer_id']: f"{r['full_name']} ({r['email']})" for _, r in customers.iterrows()}
            current_id = st.selectbox(
                "Active Customer Profile:",
                options=list(cust_dict.keys()),
                format_func=lambda x: cust_dict[x],
                index=1 if 2 in cust_dict else 0,
                help="Select customer identity for ticketing and order transactions."
            )
            st.session_state["current_customer"] = current_id
        
        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.75rem; color: #64748b; line-height: 1.6;">
            <b>Database:</b> SQLite3 ACID Engine<br>
            <b>Protection:</b> Trigger Overlap Guard Active<br>
            <b>Encryption:</b> SHA-256 Digital Barcodes
        </div>
        """, unsafe_allow_html=True)

    # Render Header & Active View
    render_hero_header()
    menu[choice]()

if __name__ == "__main__":
    main()
