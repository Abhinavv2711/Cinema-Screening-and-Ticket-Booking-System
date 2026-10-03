# Cinema Screening and Ticket Booking System
### Database Management Systems (DBMS) — Project-Based Learning (PBL)

**Student Name:** G. Abhinav  
**Roll Number:** WU0102089  
**Section:** AIML Rhinos (Batch 2025–2029)  
**Program:** B.Tech in Computer Science and Engineering (AI & ML)  
**Institution:** School of Technology, Woxsen University, Hyderabad  
**Course Faculty:** Prof. Sahithi  
**Academic Year:** 2026 – 2027  

---

## 📌 Project Overview
The **Cinema Screening and Ticket Booking System** is an enterprise-grade relational database management system designed to eliminate critical operational bottlenecks in modern multiplexes:
1. **Seat Double-Booking:** Prevented via partial unique indexes and atomic multi-row database transactions.
2. **Screen Schedule Overlap:** Prevented using database-level `BEFORE INSERT` / `BEFORE UPDATE` triggers.
3. **Uncontrolled F&B Stock Depletion:** Real-time inventory verification and automatic decrement triggers.
4. **Arbitrary Refund Disbursements:** Strict trigger enforcement preventing refunds from exceeding the original payment amount.

---

## 🛠️ Tech Stack & Environment
* **Language:** Python 3.10+
* **Database:** SQLite 3 (ANSI SQL compliant)
* **Interface:** Interactive Python CLI Terminal Application
* **Driver:** Python Standard Database API Specification (PEP 249 `sqlite3`)
* **Security:** Parameterized SQL bindings (preventing SQL injection), SHA-256 e-ticket cryptographic hashes.

---

## 🗄️ Relational Database Architecture (3NF / BCNF)
The database schema models **15 interconnected entities**:
1. `cinemas`: Multiplex locations and contact information.
2. `screens`: Auditoriums and seating capacities.
3. `seats`: Physical chairs categorized into Silver, Gold, and Platinum tiers.
4. `movies`: Film catalog with runtimes and censorship certifications.
5. `screenings`: Scheduled film time slots with overlap validation triggers.
6. `customers`: Registered customer demographic records.
7. `bookings`: Master reservation headers.
8. `booked_seats`: Active seat allocations enforcing single occupancy.
9. `tickets`: Issued e-tickets with unique serial numbers and SHA-256 barcode hashes.
10. `concession_items`: Food and beverage catalog with live stock tracking.
11. `orders`: Concession purchase order headers.
12. `order_items`: Concession order lines with strictly positive quantity constraints.
13. `payments`: Payment ledgers across UPI, Cards, Net Banking, and Cash.
14. `cancellations`: Booking voidance audit log with 10% administrative fee retention.
15. `refunds`: Refund disbursements governed by original payment ceilings.

---

## 🚀 Quick Start Guide

### 1. Clone or Extract the Repository
```bash
git clone <your-github-repo-url>
cd cinema-screening-booking-system
```

### 2. Initialize the Database Schema & Triggers
```bash
python3 project/sql/setup_db.py
```

### 3. Populate Sample Data
```bash
python3 project/sql/populate_data.py
```

### 4. Run Integrity Test Suite (10 Test Cases)
```bash
python3 project/sql/test_integrity.py
```

### 5. Launch the Application
```bash
python3 project/app/cinema_app.py
```

---

## 📊 Analytical Views Implemented
* `view_show_occupancy`: Real-time capacity utilization per screening.
* `view_movie_performance`: Total tickets sold and gross box office revenue per film.
* `view_screen_utilization`: Runtime operational hours and screen load.
* `view_concession_sales_summary`: Units sold, remaining stock, and F&B category revenue.
* `view_cancellations_and_refunds`: Cancellation audit log and fee deductions.
* `view_total_revenue_breakdown`: Net operating revenue computation.

---

## 📄 Submission Files
* **Official Project Report (PDF):** `WU0102089_G_Abhinav_DBMS_PBL_Report.pdf`
* **Official Project Report (Word DOCX):** `WU0102089_G_Abhinav_DBMS_PBL_Report.docx`

---
© 2026 G. Abhinav | Woxsen University School of Technology
