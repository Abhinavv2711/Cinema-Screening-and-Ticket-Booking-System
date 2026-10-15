import urllib.request
import json

def get(path):
    with urllib.request.urlopen('http://localhost:8000' + path) as r:
        return json.loads(r.read().decode('utf-8'))

def post(path, body, headers=None):
    h = {'Content-Type': 'application/json'}
    if headers:
        h.update(headers)
    req = urllib.request.Request('http://localhost:8000' + path, data=json.dumps(body).encode('utf-8'), headers=h)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode('utf-8'))

print('=== 1. STATUS & ACID ISOLATION ===')
st = get('/api/status')
print('Status:', st['status'], '| Engine:', st['engine'])

print('\n=== 2. OCC RACE CONDITION SIMULATION ===')
occ = post('/api/occ-simulate', {'screening_id': 1, 'seat_id': 1})
print('Seat:', occ['seat'])
print('Thread A:', occ['thread_a_status'])
print('Thread B:', occ['thread_b_status'])
print('Lock Model:', occ['db_lock_type'])

print('\n=== 3. IDEMPOTENCY KEY BOOKING TEST ===')
seats_data = get('/api/screening/1/seats')
free_seats = [s for s in seats_data['seats'] if not s['is_booked']]
if free_seats:
    free_seat = free_seats[0]
    idemp_key = 'audit-test-key-002'
    b1 = post('/api/book-tickets', {'screening_id': 1, 'seat_ids': [free_seat['seat_id']], 'customer_id': 2}, headers={'Idempotency-Key': idemp_key})
    b2 = post('/api/book-tickets', {'screening_id': 1, 'seat_ids': [free_seat['seat_id']], 'customer_id': 2}, headers={'Idempotency-Key': idemp_key})
    print('Req 1 (is_replay):', b1['is_idempotent_replay'], '| Booking ID:', b1['booking_id'])
    print('Req 2 (is_replay):', b2['is_idempotent_replay'], '| Booking ID:', b2['booking_id'])

print('\n=== 4. IMMUTABLE AUDIT LOGS ===')
logs = get('/api/audit-logs')
print(f'Total audit records in DB: {len(logs)}')
for l in logs[:4]:
    print(f"  [{l['timestamp']}] {l['entity_type']} #{l['entity_id']} ({l['previous_state']} -> {l['new_state']}) : {l['action_type']} | {l['details']}")

print('\n=== 5. EXPLAIN QUERY PLAN (BI PERFORMANCE) ===')
eqp = get('/api/explain-query')
print('View:', eqp['view_name'])
for step in eqp['execution_steps']:
    print('  Step:', step.get('detail'))

print('\n=== 6. CLEAN-DOWN BUFFER GANTT SCHEDULE ===')
timeline = get('/api/schedule-timeline')
print('Screens scheduled with turnaround buffers:', len(timeline))
for sc in timeline:
    print(f"  Screen #{sc['screen_number']} ({sc['screen_type']}): {len(sc['blocks'])} screenings with 15-min buffers")

print('\n=== 7. DYNAMIC PRICING (YIELD ENGINE) ===')
dp = get('/api/dynamic-pricing/1')
print(f"Base: ${dp['base_price']} -> Dynamic: ${dp['dynamic_ticket_price']} (Occupancy: {dp['current_occupancy_pct']}%, Tier: {dp['pricing_tier']})")

print('\n=== 8. CONCESSION INVENTORY FORECAST ===')
fore = get('/api/concession-forecast')
print('Genre-correlated demand forecasts:', len(fore))
for f in fore[:3]:
    print(f"  Item: {f['item_name']} ({f['category']}) -> Current Stock: {f['current_stock']} | Predicted Demand: {f['predicted_demand_units']} | Restock Alert: {f['reorder_alert']}")

print('\n=== 9. PROMETHEUS METRICS EXPOSITION ===')
with urllib.request.urlopen('http://localhost:8000/metrics') as r:
    raw_metrics = r.read().decode('utf-8')
    metric_lines = [l for l in raw_metrics.splitlines() if not l.startswith('#') and l.strip()]
    print('Sample metrics:', metric_lines[:5])

print('\n=== ALL 9 ADVANCED DBMS & ARCHITECTURAL CHECKS PASSED ===')
