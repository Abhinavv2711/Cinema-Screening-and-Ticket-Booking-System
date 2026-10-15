import sqlite3

conn = sqlite3.connect('cinema_booking_system_git_package/project/app/cinema_booking.db')
cur = conn.cursor()

print("ALL TABLES:")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for r in cur.fetchall():
    print(" - Table:", r[0])

print("\nALL VIEWS:")
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='view' ORDER BY name")
for r in cur.fetchall():
    print(" - View:", r[0])

print("\nALL TRIGGERS:")
cur.execute("SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name")
for r in cur.fetchall():
    print(" - Trigger:", r[0])

conn.close()
