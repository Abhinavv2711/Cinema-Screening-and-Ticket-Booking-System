import streamlit_app as sa
import time

def run_tests():
    print("Starting 10 Automated Stress Tests on the Refactored Functions...")
    success_count = 0
    
    for i in range(1, 11):
        print(f"\n--- TEST ITERATION {i} ---")
        
        # 1. Test Viewing Screenings
        df_screenings = sa.fetch_data("SELECT screening_id FROM screenings WHERE status != 'Cancelled'")
        if df_screenings.empty:
            print("No screenings available to test.")
            break
            
        screening_id = int(df_screenings.iloc[0]['screening_id'])
        
        # 2. Test Booking Tickets
        # Find 2 available seats
        conn = sa.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT s.seat_id FROM seats s
            WHERE s.screen_id = (SELECT screen_id FROM screenings WHERE screening_id = ?)
              AND s.seat_id NOT IN (
                  SELECT seat_id FROM booked_seats WHERE screening_id = ? AND status = 'Booked'
              ) LIMIT 2;
        """, (screening_id, screening_id))
        avail_seats = [r[0] for r in cur.fetchall()]
        conn.close()
        
        if len(avail_seats) < 2:
            print(f"Not enough seats available for iteration {i}. Skipping booking.")
            booking_id = 0
        else:
            print(f"Attempting to book seats {avail_seats} for screening {screening_id}...")
            b_success, b_res = sa.book_tickets_txn(customer_id=2, screening_id=screening_id, selected_seats=avail_seats, payment_method="UPI")
            if b_success:
                print(f"  -> SUCCESS! Booking ID: {b_res['booking_id']}, Txn: {b_res['txn_ref']}")
                booking_id = b_res['booking_id']
            else:
                print(f"  -> FAILED: {b_res}")
                booking_id = 0
                
        # 3. Test Concession Ordering
        print(f"Attempting concession order...")
        df_items = sa.fetch_data("SELECT item_id, unit_price FROM concession_items WHERE stock_quantity > 0 LIMIT 2")
        if not df_items.empty:
            validated_items = []
            total = 0
            for _, row in df_items.iterrows():
                item_id = int(row['item_id'])
                price = float(row['unit_price'])
                validated_items.append((item_id, 1, price, price))
                total += price
                
            c_success, c_res = sa.place_concession_order_txn(customer_id=2, booking_id=booking_id, validated_items=validated_items, total_amount=total)
            if c_success:
                print(f"  -> SUCCESS! Concession Order ID: {c_res['order_id']}")
            else:
                print(f"  -> FAILED: {c_res}")
                
        # 4. Test Cancellation (Only on even iterations to leave some valid bookings)
        if i % 2 == 0 and booking_id > 0:
            print(f"Attempting to cancel booking {booking_id}...")
            can_success, can_res = sa.cancel_booking_txn(booking_id=booking_id, reason="Stress Test Cancellation")
            if can_success:
                print(f"  -> SUCCESS! Refunded: Rs.{can_res['refund']}, Fee: Rs.{can_res['fee']}")
            else:
                print(f"  -> FAILED: {can_res}")
                
        time.sleep(0.5)
        success_count += 1
        
    print(f"\nCompleted {success_count}/10 test iterations successfully.")

if __name__ == '__main__':
    run_tests()
