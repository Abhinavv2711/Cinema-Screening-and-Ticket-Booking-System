import sqlite3

conn = sqlite3.connect('cinema_booking_system_git_package/project/app/cinema_booking.db')
cur = conn.cursor()

print("TRIGGERS:")
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
for n, s in cur.fetchall():
    print(n, "->", s)

print("\nSCREENS:")
cur.execute("SELECT screen_id, cinema_id, screen_number, screen_type, seating_capacity FROM screens")
for r in cur.fetchall():
    print(r)

print("\nEXISTING SCREENINGS:")
cur.execute("SELECT screening_id, screen_id, movie_id, show_date, start_time, end_time, ticket_price, status FROM screenings")
for r in cur.fetchall():
    print(r)

conn.close()
