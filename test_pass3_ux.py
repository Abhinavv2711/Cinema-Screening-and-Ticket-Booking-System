import urllib.request
import urllib.error
import html
import sys

BASE_URL = "http://127.0.0.1:8000"

PAGES = [
    ("/", "AURA LUXE CINEMAS", "Home / Catalog"),
    ("/movie?id=1", "Movie Details & Showtimes", "Movie 1 Details (Oppenheimer)"),
    ("/movie?id=2", "Movie Details & Showtimes", "Movie 2 Details (Dune 2)"),
    ("/booking?screening_id=1", "Select Seats & Reserve", "Auditorium Seating Matrix"),
    ("/concessions", "Gourmet Concessions & Dining", "Concessions Dining & Cart"),
    ("/my-tickets", "My Tickets & Booking Passes", "Customer Pass Wallet"),
    ("/usher", "Cinema Gate Scanner & Usher Check-In", "Staff Turnstile Station"),
    ("/admin", "Cinema Manager & Executive BI Analytics", "Executive BI & Admin Console"),
    ("/docs", "Project 65 DBMS Technical Report & Documentation", "Academic Viva Documentation")
]

def run_pass3_tests():
    passes = []
    errors = []

    print("[*] Starting Pass 3: Frontend Multi-Page UX & Route Verification")

    for path, expected_title_sub, name in PAGES:
        url = f"{BASE_URL}{path}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Antigravity-Audit/2.0"})
            with urllib.request.urlopen(req) as resp:
                status = resp.status
                raw_body = resp.read().decode("utf-8", errors="replace")
                body = html.unescape(raw_body)
                
                # Check status
                if status == 200:
                    passes.append(f"HTTP 200 OK for {name} ({path})")
                else:
                    errors.append(f"Unexpected status {status} for {path}")

                # Check expected title/content
                if expected_title_sub.lower() in body.lower():
                    passes.append(f"Title / header verified for {name}")
                else:
                    errors.append(f"Missing expected text '{expected_title_sub}' in {path}")

                # Check Tailwind CSS CDN presence
                if "cdn.tailwindcss.com" in body:
                    passes.append(f"Tailwind CSS present for {name}")
                else:
                    errors.append(f"Tailwind CDN link missing in {path}")

        except Exception as e:
            errors.append(f"Failed to fetch {path}: {e}")

    print("\n--- PASS 3 RESULTS ---")
    print(f"Passed assertions: {len(passes)}")
    for p in passes:
        print(f"  [+] {p}")
    if errors:
        print(f"\nFailed assertions: {len(errors)}")
        for e in errors:
            print(f"  [-] {e}")
        return False
    else:
        print("\nAll Pass 3 Frontend Multi-Page UX tests PASSED successfully!")
        return True

if __name__ == "__main__":
    success = run_pass3_tests()
    sys.exit(0 if success else 1)
