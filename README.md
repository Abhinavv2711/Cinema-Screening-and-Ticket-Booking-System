# AURA LUXE CINEMAS — Screening & Ticket Booking Engine
> **Project 65: Comprehensive DBMS PBL & High-Performance Theatrical Exhibition Engine**

A production-grade, ACID-compliant **Cinema Screening & Ticket Booking Engine** built with **FastAPI**, **SQLite3**, and a zero-build **Tailwind CSS** modernist frontend. Designed for real-world cinema operations with multi-screen conflict prevention, real-time seat locking, dynamic pricing yield management, and staff turnstile admission.

---

## 🌟 Key Highlights & Engineering Features

### 1. Database & ACID Integrity Hardening (SQLite3)
- **Zero-Overlap Turnaround Enforcement:** SQL `BEFORE INSERT` and `BEFORE UPDATE` triggers prevent screenings from overlapping on the same screen while mandating a 15-minute auditorium cleanup/turnaround buffer.
- **Seat Race Condition Protection:** High-performance partial unique index `uq_screening_seat_active` prevents double-booking at the database engine level.
- **Optimistic Concurrency Control (OCC):** `version_id` column on seats and tickets to detect and prevent mid-air collisions when multiple clients reserve the same seat simultaneously.
- **Excessive Refund Limit Trigger:** `trg_check_refund_limit` ensures refund amounts never exceed original payment amounts.
- **Multi-Date 7-Day Theatrical Schedule:** 92 scheduled screenings spanning 7 consecutive dates across 3 multiplexes and 6 screens (IMAX 3D Laser, Gold VIP Recliner, 4DX Motion).
- **6 Analytical SQL Views:**
  1. `view_show_occupancy`: Real-time hall saturation metrics.
  2. `view_movie_performance`: Box office gross and ticket volume per film.
  3. `view_screen_utilization`: Screen hours and downtime efficiency.
  4. `view_total_revenue_breakdown`: Box office vs. concessions revenue split.
  5. `view_concession_sales_summary`: Top-selling snacks and beverage performance.
  6. `view_cancellations_and_refunds`: 90% refund policy tracking and audit logs.

### 2. Backend & API Resilience (FastAPI)
- **Idempotency Keys:** `Idempotency-Key` header prevents duplicate reservations or double-charging during client retries.
- **Sliding-Window Rate Limiting:** Prevents seat-hoarding bots on booking and checkout endpoints.
- **Dynamic Pricing Engine:** Adjusts ticket pricing based on auditorium occupancy saturation and release format.
- **Predictive Concession Inventory Forecast:** Correlates genre attendance with snack demand to alert when inventory reaches restock thresholds.
- **Prometheus Telemetry (/metrics):** Live metrics format tracking transaction latency, connection pool status, and throughput.

### 3. Frontend Architecture
Built using clean, modern HTML5 and Tailwind CSS:
- Responsive user interface with interactive SVG auditorium seat matrix and live booking workflow.
- Dedicated interfaces for movie discovery, gourmet concessions ordering, digital pass wallet, and management analytics.

---

## 📑 Dedicated Landing Pages

| Page | URL Path | Description |
| :--- | :--- | :--- |
| **Cinema Home & Catalog** | `/` | Showcase hero, 7-day showtime discovery bar, genre filters, and movie gallery |
| **Movie Details & Showtimes** | `/movie?id=1` | 7-day pill calendar, format badges (IMAX, 4DX, Dolby), cast, and showtimes |
| **Auditorium Seating Matrix** | `/booking?screening_id=1` | Interactive SVG curved screen, dynamic pricing tier, add-on snacks, and pass |
| **Gourmet Concessions Dining**| `/concessions` | Food & beverage menu, stock tracker, and live shopping cart drawer |
| **Customer Pass Wallet** | `/my-tickets` | Scannable digital boarding passes and 1-click 90% refund engine |
| **Staff Turnstile Scanner** | `/usher` | Usher turnstile admission station with double-entry prevention |
| **Executive BI & Admin Console**| `/admin` | 6 SQL views, OCC concurrency simulator, and B-Tree `EXPLAIN QUERY PLAN` |
| **Academic Viva Documentation**| `/docs` | Comprehensive project viva notes, relational schema, and trigger definitions |

---

## 🚀 Quickstart

### 1. Requirements
- Python 3.9+
- Dependencies: `fastapi`, `uvicorn`, `pydantic`

```bash
pip install fastapi uvicorn pydantic
```

### 2. Start the Server
```bash
python -m uvicorn cinema_server:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at **`http://localhost:8000/`**.

---

## 🏛️ Academic PBL Context
- **Project Title:** Design and Implementation of a Database Management System for Cinema Screening and Ticket Booking System
- **Student Name:** G. Abhinav
- **Roll Number:** WU0102089 (25WU0102089)
- **Section:** AIML Rhinos (Batch 2025–2029)
- **Program:** B.Tech in Computer Science and Engineering
- **Institution:** School of Technology, Woxsen University, Hyderabad
- **Course:** Database Management Systems (DBMS PBL)
- **Course Faculty:** Prof. Sahithi
- **Academic Year:** 2026 – 2027