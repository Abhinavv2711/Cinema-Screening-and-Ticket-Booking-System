import urllib.request

routes = [
    '/',
    '/movie?id=1',
    '/booking?screening_id=1',
    '/concessions',
    '/my-tickets',
    '/usher',
    '/admin',
    '/docs',
    '/api/screenings',
    '/api/cinemas',
    '/api/screens',
    '/api/reports',
    '/metrics'
]

passed = 0
for r in routes:
    try:
        resp = urllib.request.urlopen('http://localhost:8000' + r)
        print(f"[OK] {r} -> {resp.status}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {r} -> {e}")

print(f"\nSummary: {passed}/{len(routes)} pages and endpoints returned HTTP 200 OK!")
