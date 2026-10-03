import sqlite3
import hashlib
import datetime

conn = sqlite3.connect('/tmp/cinema_booking.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# 1. Cinemas
cinemas_data = [
    (1, 'PVR Inorbit Cyberabad', 'Hyderabad', 'Inorbit Mall, Mindspace, HITEC City, Hyderabad', 5, '+91-40-23456789', 'support.inorbit@pvrcinemas.com'),
    (2, 'INOX GVK One', 'Hyderabad', 'GVK One Mall, Rd Number 1, Banjara Hills, Hyderabad', 6, '+91-40-67891234', 'manager.gvk@inoxmovies.com'),
    (3, 'Cinepolis Forum Sujana', 'Hyderabad', 'Forum Sujana Mall, K P H B Phase 9, Kukatpally, Hyderabad', 7, '+91-40-45678901', 'contact.forum@cinepolis.com')
]
cursor.executemany("INSERT INTO cinemas VALUES (?,?,?,?,?,?,?)", cinemas_data)

# 2. Screens
screens_data = [
    (1, 1, 1, 'IMAX 3D', 50),
    (2, 1, 2, 'Standard', 40),
    (3, 1, 3, 'Gold VIP', 20),
    (4, 2, 1, 'Standard', 40),
    (5, 2, 2, '4DX', 30),
    (6, 3, 1, 'Standard', 50)
]
cursor.executemany("INSERT INTO screens VALUES (?,?,?,?,?)", screens_data)

# 3. Seats (Generate realistic rows for screens)
seats_data = []
seat_id_counter = 1
for screen_id, _, _, s_type, cap in screens_data:
    rows = ['A', 'B', 'C', 'D', 'E']
    seats_per_row = cap // len(rows)
    for r_idx, row in enumerate(rows):
        tier = 'Silver' if r_idx < 2 else ('Gold' if r_idx < 4 else 'Platinum')
        base_p = 150.0 if tier == 'Silver' else (250.0 if tier == 'Gold' else 400.0)
        if s_type == 'IMAX 3D':
            base_p += 150.0
        elif s_type == 'Gold VIP':
            base_p += 300.0
        elif s_type == '4DX':
            base_p += 200.0
            
        for s_num in range(1, seats_per_row + 1):
            seats_data.append((seat_id_counter, screen_id, row, s_num, tier, base_p))
            seat_id_counter += 1

cursor.executemany("INSERT INTO seats VALUES (?,?,?,?,?,?)", seats_data)

# 4. Movies
movies_data = [
    (1, 'Oppenheimer', 'Biography/Drama', 180, 'UA', '2023-07-21', 'English'),
    (2, 'Dune: Part Two', 'Sci-Fi/Adventure', 166, 'UA', '2024-03-01', 'English'),
    (3, 'Interstellar', 'Sci-Fi/Drama', 169, 'UA', '2014-11-07', 'English'),
    (4, 'Kalki 2898 AD', 'Sci-Fi/Mythology', 181, 'UA', '2024-06-27', 'Telugu'),
    (5, 'Inception', 'Action/Sci-Fi', 148, 'UA', '2010-07-16', 'English')
]
cursor.executemany("INSERT INTO movies VALUES (?,?,?,?,?,?,?)", movies_data)

# 5. Screenings (Carefully scheduled with NO overlaps)
screenings_data = [
    (1, 1, 1, '2026-10-04', '10:00', '13:15', 450.00, 'Scheduled'),
    (2, 1, 2, '2026-10-04', '14:00', '17:00', 480.00, 'Scheduled'),
    (3, 1, 4, '2026-10-04', '18:00', '21:15', 500.00, 'Scheduled'),
    (4, 2, 3, '2026-10-04', '11:00', '14:00', 250.00, 'Scheduled'),
    (5, 2, 5, '2026-10-04', '15:00', '17:45', 250.00, 'Scheduled'),
    (6, 3, 1, '2026-10-04', '18:30', '21:45', 750.00, 'Scheduled'),
    (7, 4, 4, '2026-10-04', '10:30', '13:45', 220.00, 'Scheduled'),
    (8, 5, 2, '2026-10-04', '16:00', '19:00', 450.00, 'Scheduled')
]
cursor.executemany("INSERT INTO screenings VALUES (?,?,?,?,?,?,?,?)", screenings_data)

# 6. Customers
customers_data = [
    (1, 'Rahul Sharma', 'rahul.sharma@gmail.com', '+91-9876543210'),
    (2, 'Priya Reddy', 'priya.reddy@yahoo.com', '+91-9876543211'),
    (3, 'Ananya Verma', 'ananya.v@outlook.com', '+91-9876543212'),
    (4, 'Vikram Malhotra', 'vikram.m@gmail.com', '+91-9876543213'),
    (5, 'Siddharth Rao', 'siddharth.rao@gmail.com', '+91-9876543214'),
    (6, 'Neha Patel', 'neha.patel@hotmail.com', '+91-9876543215')
]
cursor.executemany("INSERT INTO customers (customer_id, full_name, email, phone) VALUES (?,?,?,?)", customers_data)

# 7. Bookings
bookings_data = [
    (1, 1, 1, '2026-10-03 10:15:00', 900.00, 'Confirmed'),
    (2, 2, 1, '2026-10-03 11:30:00', 450.00, 'Confirmed'),
    (3, 3, 2, '2026-10-03 14:00:00', 960.00, 'Confirmed'),
    (4, 4, 3, '2026-10-03 15:45:00', 500.00, 'Cancelled'),
    (5, 5, 6, '2026-10-03 16:20:00', 1500.00, 'Confirmed'),
    (6, 6, 4, '2026-10-03 17:10:00', 500.00, 'Confirmed')
]
cursor.executemany("INSERT INTO bookings VALUES (?,?,?,?,?,?)", bookings_data)

# 8. Booked Seats
booked_seats_data = [
    # Booking 1: 2 seats on screening 1 (Screen 1, seats 1, 2)
    (1, 1, 1, 1, 450.00, 'Booked'),
    (2, 1, 1, 2, 450.00, 'Booked'),
    # Booking 2: 1 seat on screening 1 (seat 3)
    (3, 2, 1, 3, 450.00, 'Booked'),
    # Booking 3: 2 seats on screening 2 (Screen 1, seats 11, 12)
    (4, 3, 2, 11, 480.00, 'Booked'),
    (5, 3, 2, 12, 480.00, 'Booked'),
    # Booking 4: 1 seat on screening 3 (Screen 1, seat 21) - Cancelled
    (6, 4, 3, 21, 500.00, 'Cancelled'),
    # Booking 5: 2 seats on screening 6 (Screen 3, seats 91, 92)
    (7, 5, 6, 91, 750.00, 'Booked'),
    (8, 5, 6, 92, 750.00, 'Booked'),
    # Booking 6: 2 seats on screening 4 (Screen 2, seats 51, 52)
    (9, 6, 4, 51, 250.00, 'Booked'),
    (10, 6, 4, 52, 250.00, 'Booked')
]
cursor.executemany("INSERT INTO booked_seats VALUES (?,?,?,?,?,?)", booked_seats_data)

# 9. Tickets
tickets_data = [
    (1, 1, 1, 'TKT-2026-00101', '2026-10-03 10:15:05', hashlib.sha256(b'TKT-2026-00101').hexdigest()[:16], 'Active'),
    (2, 1, 2, 'TKT-2026-00102', '2026-10-03 10:15:05', hashlib.sha256(b'TKT-2026-00102').hexdigest()[:16], 'Active'),
    (3, 2, 3, 'TKT-2026-00103', '2026-10-03 11:30:05', hashlib.sha256(b'TKT-2026-00103').hexdigest()[:16], 'Active'),
    (4, 3, 4, 'TKT-2026-00104', '2026-10-03 14:00:05', hashlib.sha256(b'TKT-2026-00104').hexdigest()[:16], 'Active'),
    (5, 3, 5, 'TKT-2026-00105', '2026-10-03 14:00:05', hashlib.sha256(b'TKT-2026-00105').hexdigest()[:16], 'Active'),
    (6, 4, 6, 'TKT-2026-00106', '2026-10-03 15:45:05', hashlib.sha256(b'TKT-2026-00106').hexdigest()[:16], 'Cancelled'),
    (7, 5, 7, 'TKT-2026-00107', '2026-10-03 16:20:05', hashlib.sha256(b'TKT-2026-00107').hexdigest()[:16], 'Active'),
    (8, 5, 8, 'TKT-2026-00108', '2026-10-03 16:20:05', hashlib.sha256(b'TKT-2026-00108').hexdigest()[:16], 'Active'),
    (9, 6, 9, 'TKT-2026-00109', '2026-10-03 17:10:05', hashlib.sha256(b'TKT-2026-00109').hexdigest()[:16], 'Active'),
    (10, 6, 10, 'TKT-2026-00110', '2026-10-03 17:10:05', hashlib.sha256(b'TKT-2026-00110').hexdigest()[:16], 'Active')
]
cursor.executemany("INSERT INTO tickets VALUES (?,?,?,?,?,?,?)", tickets_data)

# 10. Concession Items
concession_items_data = [
    (1, 'Large Caramel Popcorn', 'Popcorn', 350.00, 150),
    (2, 'Regular Salted Popcorn', 'Popcorn', 250.00, 200),
    (3, 'Coca Cola (500ml)', 'Beverage', 150.00, 300),
    (4, 'Mineral Water (1L)', 'Beverage', 60.00, 250),
    (5, 'Crispy Nachos with Salsa & Cheese', 'Snack', 280.00, 120),
    (6, 'Gourmet Chicken Burger Combo', 'Combo', 450.00, 80),
    (7, 'Classic Veg Puff', 'Snack', 120.00, 100)
]
cursor.executemany("INSERT INTO concession_items VALUES (?,?,?,?,?)", concession_items_data)

# 11. Orders (Concession Orders)
orders_data = [
    (1, 1, 1, '2026-10-03 10:20:00', 500.00, 'Delivered'),
    (2, 3, 3, '2026-10-03 14:05:00', 630.00, 'Delivered'),
    (3, 5, 5, '2026-10-03 16:25:00', 800.00, 'Prepared'),
    (4, None, 2, '2026-10-03 18:00:00', 350.00, 'Delivered')
]
cursor.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", orders_data)

# 12. Order Items
order_items_data = [
    (1, 1, 1, 1, 350.00, 350.00), # 1x Large Caramel Popcorn
    (2, 1, 3, 1, 150.00, 150.00), # 1x Coca Cola
    (3, 2, 1, 1, 350.00, 350.00), # 1x Large Caramel Popcorn
    (4, 2, 5, 1, 280.00, 280.00), # 1x Nachos
    (5, 3, 1, 1, 350.00, 350.00), # 1x Large Caramel Popcorn
    (6, 3, 6, 1, 450.00, 450.00), # 1x Burger Combo
    (7, 4, 1, 1, 350.00, 350.00)  # 1x Large Caramel Popcorn
]
cursor.executemany("INSERT INTO order_items VALUES (?,?,?,?,?,?)", order_items_data)

# 13. Payments
payments_data = [
    # Ticket Payments
    (1, 1, None, '2026-10-03 10:15:10', 900.00, 'UPI', 'TXN-UPI-982347101', 'Success'),
    (2, 2, None, '2026-10-03 11:30:10', 450.00, 'Credit Card', 'TXN-CC-192837402', 'Success'),
    (3, 3, None, '2026-10-03 14:00:10', 960.00, 'Debit Card', 'TXN-DC-837461903', 'Success'),
    (4, 4, None, '2026-10-03 15:45:10', 500.00, 'UPI', 'TXN-UPI-482910304', 'Refunded'),
    (5, 5, None, '2026-10-03 16:20:10', 1500.00, 'Net Banking', 'TXN-NB-384729105', 'Success'),
    (6, 6, None, '2026-10-03 17:10:10', 500.00, 'UPI', 'TXN-UPI-593820106', 'Success'),
    # Concession Payments
    (7, None, 1, '2026-10-03 10:20:10', 500.00, 'UPI', 'TXN-UPI-CONC-001', 'Success'),
    (8, None, 2, '2026-10-03 14:05:10', 630.00, 'Credit Card', 'TXN-CC-CONC-002', 'Success'),
    (9, None, 3, '2026-10-03 16:25:10', 800.00, 'UPI', 'TXN-UPI-CONC-003', 'Success'),
    (10, None, 4, '2026-10-03 18:00:10', 350.00, 'Cash', 'TXN-CSH-CONC-004', 'Success')
]
cursor.executemany("INSERT INTO payments VALUES (?,?,?,?,?,?,?,?)", payments_data)

# 14. Cancellations (Booking 4 cancelled, fee Rs 50, refund Rs 450)
cancellations_data = [
    (1, 4, '2026-10-03 16:00:00', 'Customer urgent schedule conflict', 50.00, 'Processed')
]
cursor.executemany("INSERT INTO cancellations VALUES (?,?,?,?,?,?)", cancellations_data)

# 15. Refunds (Payment 4 refunded Rs 450, within original amount 500)
refunds_data = [
    (1, 1, 4, 450.00, '2026-10-03 16:05:00', 'REF-UPI-2026-4001', 'Processed')
]
cursor.executemany("INSERT INTO refunds VALUES (?,?,?,?,?,?,?)", refunds_data)

conn.commit()
print("Sample data populated successfully.")
conn.close()
