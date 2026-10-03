import sqlite3
import os

db_path = "/tmp/cinema_booking.db"
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

ddl_script = """
-- 1. Cinemas Table
CREATE TABLE cinemas (
    cinema_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    total_screens INTEGER NOT NULL CHECK (total_screens > 0),
    contact_phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Screens Table
CREATE TABLE screens (
    screen_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cinema_id INTEGER NOT NULL,
    screen_number INTEGER NOT NULL,
    screen_type VARCHAR(20) NOT NULL CHECK (screen_type IN ('Standard', 'IMAX 3D', '4DX', 'Gold VIP')),
    seating_capacity INTEGER NOT NULL CHECK (seating_capacity > 0),
    FOREIGN KEY (cinema_id) REFERENCES cinemas(cinema_id) ON DELETE CASCADE,
    UNIQUE (cinema_id, screen_number)
);

-- 3. Seats Table
CREATE TABLE seats (
    seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    screen_id INTEGER NOT NULL,
    row_label VARCHAR(5) NOT NULL,
    seat_number INTEGER NOT NULL CHECK (seat_number > 0),
    seat_tier VARCHAR(20) NOT NULL CHECK (seat_tier IN ('Silver', 'Gold', 'Platinum')),
    base_price DECIMAL(8,2) NOT NULL CHECK (base_price >= 0),
    FOREIGN KEY (screen_id) REFERENCES screens(screen_id) ON DELETE CASCADE,
    UNIQUE (screen_id, row_label, seat_number)
);

-- 4. Movies Table
CREATE TABLE movies (
    movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(150) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    rating VARCHAR(10) NOT NULL CHECK (rating IN ('U', 'UA', 'A', 'R')),
    release_date DATE NOT NULL,
    language VARCHAR(30) NOT NULL
);

-- 5. Screenings Table
CREATE TABLE screenings (
    screening_id INTEGER PRIMARY KEY AUTOINCREMENT,
    screen_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    show_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    ticket_price DECIMAL(8,2) NOT NULL CHECK (ticket_price > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Running', 'Completed', 'Cancelled')),
    FOREIGN KEY (screen_id) REFERENCES screens(screen_id) ON DELETE RESTRICT,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE RESTRICT,
    CHECK (start_time < end_time)
);

-- Trigger: Enforce No Screen Overlap on Screenings
CREATE TRIGGER trg_prevent_screen_overlap_insert
BEFORE INSERT ON screenings
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Integrity Violation: Screen overlap detected for the designated screen and time.')
    WHERE EXISTS (
        SELECT 1 FROM screenings
        WHERE screen_id = NEW.screen_id
          AND show_date = NEW.show_date
          AND status != 'Cancelled'
          AND (
              (NEW.start_time >= start_time AND NEW.start_time < end_time) OR
              (NEW.end_time > start_time AND NEW.end_time <= end_time) OR
              (NEW.start_time <= start_time AND NEW.end_time >= end_time)
          )
    );
END;

CREATE TRIGGER trg_prevent_screen_overlap_update
BEFORE UPDATE OF screen_id, show_date, start_time, end_time, status ON screenings
FOR EACH ROW
WHEN NEW.status != 'Cancelled'
BEGIN
    SELECT RAISE(ABORT, 'Integrity Violation: Screen overlap detected for the designated screen and time.')
    WHERE EXISTS (
        SELECT 1 FROM screenings
        WHERE screen_id = NEW.screen_id
          AND show_date = NEW.show_date
          AND screening_id != NEW.screening_id
          AND status != 'Cancelled'
          AND (
              (NEW.start_time >= start_time AND NEW.start_time < end_time) OR
              (NEW.end_time > start_time AND NEW.end_time <= end_time) OR
              (NEW.start_time <= start_time AND NEW.end_time >= end_time)
          )
    );
END;

-- 6. Customers Table
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Bookings Table
CREATE TABLE bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    screening_id INTEGER NOT NULL,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0),
    booking_status VARCHAR(20) NOT NULL DEFAULT 'Confirmed' CHECK (booking_status IN ('Confirmed', 'Cancelled', 'Completed')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (screening_id) REFERENCES screenings(screening_id) ON DELETE RESTRICT
);

-- 8. Booked Seats Table
CREATE TABLE booked_seats (
    booked_seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    screening_id INTEGER NOT NULL,
    seat_id INTEGER NOT NULL,
    price DECIMAL(8,2) NOT NULL CHECK (price >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'Booked' CHECK (status IN ('Booked', 'Cancelled')),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (screening_id) REFERENCES screenings(screening_id) ON DELETE RESTRICT,
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id) ON DELETE RESTRICT
);

-- Unique index enforcing: One seat per screening for active bookings!
CREATE UNIQUE INDEX uq_screening_seat_active 
ON booked_seats(screening_id, seat_id) 
WHERE status = 'Booked';

-- 9. Tickets Table
CREATE TABLE tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    booked_seat_id INTEGER NOT NULL UNIQUE,
    ticket_number VARCHAR(50) NOT NULL UNIQUE,
    issue_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    barcode_hash VARCHAR(64) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Cancelled', 'Used')),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (booked_seat_id) REFERENCES booked_seats(booked_seat_id) ON DELETE RESTRICT
);

-- 10. Concession Items Table
CREATE TABLE concession_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(30) NOT NULL CHECK (category IN ('Popcorn', 'Beverage', 'Snack', 'Combo')),
    unit_price DECIMAL(8,2) NOT NULL CHECK (unit_price > 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0)
);

-- 11. Orders Table (Concession Orders)
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER,
    customer_id INTEGER NOT NULL,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0),
    order_status VARCHAR(20) NOT NULL DEFAULT 'Placed' CHECK (order_status IN ('Placed', 'Prepared', 'Delivered', 'Cancelled')),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
);

-- 12. Order Items Table
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(8,2) NOT NULL CHECK (unit_price > 0),
    subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal > 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES concession_items(item_id) ON DELETE RESTRICT
);

-- 13. Payments Table
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER,
    order_id INTEGER,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Cash')),
    transaction_reference VARCHAR(64) NOT NULL UNIQUE,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Success' CHECK (payment_status IN ('Success', 'Failed', 'Refunded')),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE RESTRICT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE RESTRICT,
    CHECK (booking_id IS NOT NULL OR order_id IS NOT NULL)
);

-- 14. Cancellations Table
CREATE TABLE cancellations (
    cancellation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL UNIQUE,
    cancellation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT NOT NULL,
    cancellation_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK (cancellation_fee >= 0),
    refund_status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (refund_status IN ('Pending', 'Approved', 'Processed', 'Rejected')),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE RESTRICT
);

-- 15. Refunds Table
CREATE TABLE refunds (
    refund_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cancellation_id INTEGER NOT NULL UNIQUE,
    payment_id INTEGER NOT NULL,
    refund_amount DECIMAL(10,2) NOT NULL CHECK (refund_amount > 0),
    refund_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    refund_reference VARCHAR(64) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'Processed' CHECK (status IN ('Pending', 'Processed', 'Failed')),
    FOREIGN KEY (cancellation_id) REFERENCES cancellations(cancellation_id) ON DELETE RESTRICT,
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE RESTRICT
);

-- Trigger: Enforce Refund Limit (Refund Amount cannot exceed Payment Amount)
CREATE TRIGGER trg_check_refund_limit
BEFORE INSERT ON refunds
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Integrity Violation: Refund amount cannot exceed original payment amount.')
    WHERE NEW.refund_amount > (SELECT amount FROM payments WHERE payment_id = NEW.payment_id);
END;

-- ============================================================================
-- REPORTING VIEWS
-- ============================================================================

-- View 1: Show Occupancy
CREATE VIEW view_show_occupancy AS
SELECT 
    s.screening_id,
    c.name AS cinema_name,
    sc.screen_number,
    sc.screen_type,
    m.title AS movie_title,
    s.show_date,
    s.start_time,
    sc.seating_capacity AS total_seats,
    COUNT(bs.booked_seat_id) AS booked_seats,
    (sc.seating_capacity - COUNT(bs.booked_seat_id)) AS available_seats,
    ROUND((COUNT(bs.booked_seat_id) * 100.0 / sc.seating_capacity), 2) AS occupancy_percentage
FROM screenings s
JOIN screens sc ON s.screen_id = sc.screen_id
JOIN cinemas c ON sc.cinema_id = c.cinema_id
JOIN movies m ON s.movie_id = m.movie_id
LEFT JOIN booked_seats bs ON s.screening_id = bs.screening_id AND bs.status = 'Booked'
GROUP BY s.screening_id, c.name, sc.screen_number, sc.screen_type, m.title, s.show_date, s.start_time, sc.seating_capacity;

-- View 2: Movie Performance
CREATE VIEW view_movie_performance AS
SELECT 
    m.movie_id,
    m.title AS movie_title,
    m.genre,
    m.language,
    COUNT(DISTINCT s.screening_id) AS total_screenings,
    COUNT(t.ticket_id) AS tickets_sold,
    COALESCE(SUM(bs.price), 0.00) AS box_office_gross
FROM movies m
LEFT JOIN screenings s ON m.movie_id = s.movie_id
LEFT JOIN bookings b ON s.screening_id = b.screening_id AND b.booking_status != 'Cancelled'
LEFT JOIN booked_seats bs ON b.booking_id = bs.booking_id AND bs.status = 'Booked'
LEFT JOIN tickets t ON bs.booked_seat_id = t.booked_seat_id AND t.status != 'Cancelled'
GROUP BY m.movie_id, m.title, m.genre, m.language;

-- View 3: Screen Utilization
CREATE VIEW view_screen_utilization AS
SELECT 
    c.name AS cinema_name,
    sc.screen_id,
    sc.screen_number,
    sc.screen_type,
    sc.seating_capacity,
    COUNT(s.screening_id) AS total_shows_scheduled,
    COALESCE(SUM(m.duration_minutes) / 60.0, 0.0) AS operational_hours_runtime,
    COALESCE(SUM(CASE WHEN bs.status = 'Booked' THEN 1 ELSE 0 END), 0) AS total_admissions,
    ROUND(COALESCE(SUM(CASE WHEN bs.status = 'Booked' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(s.screening_id) * sc.seating_capacity, 0), 0), 2) AS average_capacity_utilization
FROM screens sc
JOIN cinemas c ON sc.cinema_id = c.cinema_id
LEFT JOIN screenings s ON sc.screen_id = s.screen_id AND s.status != 'Cancelled'
LEFT JOIN movies m ON s.movie_id = m.movie_id
LEFT JOIN booked_seats bs ON s.screening_id = bs.screening_id
GROUP BY c.name, sc.screen_id, sc.screen_number, sc.screen_type, sc.seating_capacity;

-- View 4: Concession Sales Summary
CREATE VIEW view_concession_sales_summary AS
SELECT 
    ci.item_id,
    ci.item_name,
    ci.category,
    ci.unit_price,
    ci.stock_quantity AS current_stock,
    COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
    COALESCE(SUM(oi.subtotal), 0.00) AS total_revenue
FROM concession_items ci
LEFT JOIN order_items oi ON ci.item_id = oi.item_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status != 'Cancelled'
GROUP BY ci.item_id, ci.item_name, ci.category, ci.unit_price, ci.stock_quantity;

-- View 5: Cancellations and Refunds
CREATE VIEW view_cancellations_and_refunds AS
SELECT 
    c.cancellation_id,
    b.booking_id,
    cust.full_name AS customer_name,
    m.title AS movie_title,
    s.show_date,
    b.total_amount AS booking_amount,
    c.cancellation_fee,
    r.refund_amount,
    c.reason,
    c.cancellation_time,
    r.refund_reference
FROM cancellations c
JOIN bookings b ON c.booking_id = b.booking_id
JOIN customers cust ON b.customer_id = cust.customer_id
JOIN screenings s ON b.screening_id = s.screening_id
JOIN movies m ON s.movie_id = m.movie_id
LEFT JOIN refunds r ON c.cancellation_id = r.cancellation_id;

-- View 6: Total Revenue Breakdown
CREATE VIEW view_total_revenue_breakdown AS
SELECT 
    c.name AS cinema_name,
    COALESCE(SUM(CASE WHEN p.booking_id IS NOT NULL AND p.payment_status = 'Success' THEN p.amount ELSE 0 END), 0.00) AS ticket_revenue,
    COALESCE(SUM(CASE WHEN p.order_id IS NOT NULL AND p.payment_status = 'Success' THEN p.amount ELSE 0 END), 0.00) AS concession_revenue,
    COALESCE(SUM(canc.cancellation_fee), 0.00) AS cancellation_penalties_retained,
    COALESCE(SUM(ref.refund_amount), 0.00) AS total_refunds_disbursed,
    (
        COALESCE(SUM(CASE WHEN p.booking_id IS NOT NULL AND p.payment_status = 'Success' THEN p.amount ELSE 0 END), 0.00) +
        COALESCE(SUM(CASE WHEN p.order_id IS NOT NULL AND p.payment_status = 'Success' THEN p.amount ELSE 0 END), 0.00) +
        COALESCE(SUM(canc.cancellation_fee), 0.00) -
        COALESCE(SUM(ref.refund_amount), 0.00)
    ) AS net_operating_revenue
FROM cinemas c
LEFT JOIN screens sc ON c.cinema_id = sc.cinema_id
LEFT JOIN screenings s ON sc.screen_id = s.screen_id
LEFT JOIN bookings b ON s.screening_id = b.screening_id
LEFT JOIN payments p ON b.booking_id = p.booking_id
LEFT JOIN cancellations canc ON b.booking_id = canc.booking_id
LEFT JOIN refunds ref ON canc.cancellation_id = ref.cancellation_id
GROUP BY c.name;
"""

cursor.executescript(ddl_script)
conn.commit()
print("DDL and Views successfully created.")
conn.close()
