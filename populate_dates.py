import sqlite3

conn = sqlite3.connect('cinema_booking_system_git_package/project/app/cinema_booking.db')
cur = conn.cursor()

dates = ['2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08', '2026-10-09', '2026-10-10']

screenings_template = [
    # Screen 1 (IMAX 3D, Cinema 1)
    (1, 1, '10:00', '13:15', 450),
    (1, 2, '14:00', '17:00', 480),
    (1, 4, '18:00', '21:15', 500),
    # Screen 2 (Standard, Cinema 1)
    (2, 3, '11:00', '14:00', 250),
    (2, 5, '15:00', '17:45', 250),
    (2, 2, '18:30', '21:30', 260),
    # Screen 3 (Gold VIP, Cinema 1)
    (3, 1, '14:00', '17:15', 750),
    (3, 1, '18:30', '21:45', 750),
    # Screen 4 (Standard, Cinema 2)
    (4, 4, '10:30', '13:45', 220),
    (4, 3, '14:30', '17:30', 240),
    (4, 5, '18:15', '21:00', 240),
    # Screen 5 (4DX, Cinema 2)
    (5, 2, '12:00', '15:00', 450),
    (5, 2, '16:00', '19:00', 450),
    (5, 4, '19:45', '23:00', 480),
]

inserted = 0
for d in dates:
    for screen_id, movie_id, start_t, end_t, price in screenings_template:
        try:
            cur.execute("""
                INSERT INTO screenings (screen_id, movie_id, show_date, start_time, end_time, ticket_price, status)
                VALUES (?, ?, ?, ?, ?, ?, 'Scheduled');
            """, (screen_id, movie_id, d, start_t, end_t, price))
            inserted += 1
        except Exception as e:
            print(f"Error on {d} screen {screen_id}: {e}")

conn.commit()
print(f"Successfully inserted {inserted} new screenings across {len(dates)} dates!")

# Verify count by date
cur.execute("SELECT show_date, COUNT(*) FROM screenings GROUP BY show_date ORDER BY show_date;")
for r in cur.fetchall():
    print("Date:", r[0], "-> Total Screenings:", r[1])

conn.close()
