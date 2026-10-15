/**
 * Universal Database & API Bridge
 * Enables seamless interaction both with the live FastAPI SQLite3 backend
 * and as an interactive, fully offline/GitHub Pages static demonstration.
 */
(function () {
  const origFetch = window.fetch.bind(window);
  let staticData = null;

  async function getStaticData() {
    if (staticData) return staticData;
    try {
      const res = await origFetch('api_data.json');
      if (res.ok) {
        staticData = await res.json();
        return staticData;
      }
    } catch (e) {
      console.warn("Could not load api_data.json:", e);
    }
    return null;
  }

  function getLocalBookings() {
    try {
      const stored = localStorage.getItem('aura_cinema_bookings');
      return stored ? JSON.parse(stored) : [];
    } catch (e) {
      return [];
    }
  }

  function saveLocalBooking(bkg) {
    const list = getLocalBookings();
    list.unshift(bkg);
    localStorage.setItem('aura_cinema_bookings', JSON.stringify(list));
  }

  function createJsonResponse(obj, status = 200) {
    return new Response(JSON.stringify(obj), {
      status: status,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  window.fetch = async function (input, init = {}) {
    const urlStr = typeof input === 'string' ? input : (input.url || '');
    const method = (init.method || 'GET').toUpperCase();

    // 1. First, attempt live server request
    try {
      const res = await origFetch(input, init);
      // If server is reachable and returned a valid response, return it
      if (res.status !== 404 && res.status !== 502 && res.status !== 503) {
        return res;
      }
    } catch (err) {
      // Server is offline (e.g., hosted on GitHub Pages) - fallback gracefully
    }

    // 2. Only intercept /api/ requests for client-side fallback
    if (!urlStr.includes('/api/')) {
      return origFetch(input, init);
    }

    const data = await getStaticData();
    if (!data) {
      return createJsonResponse({ error: "Backend server unavailable and offline dataset not loaded." }, 503);
    }

    // --- Route Matching ---

    // GET /api/movies
    if (urlStr.includes('/api/movies')) {
      return createJsonResponse(data.movies);
    }

    // GET /api/screenings
    if (urlStr.includes('/api/screenings')) {
      let filtered = [...data.screenings];
      if (urlStr.includes('movie_id=')) {
        const mid = parseInt(urlStr.split('movie_id=')[1].split('&')[0]);
        filtered = filtered.filter(s => s.movie_id === mid);
      }
      return createJsonResponse(filtered);
    }

    // GET /api/movie/{id}
    if (urlStr.match(/\/api\/movie\/\d+/)) {
      const idMatch = urlStr.match(/\/api\/movie\/(\d+)/);
      const mid = idMatch ? parseInt(idMatch[1]) : 1;
      const movie = data.movies.find(m => m.movie_id === mid) || data.movies[0];
      const screenings = data.screenings.filter(s => s.movie_id === mid);
      return createJsonResponse({ movie, screenings });
    }

    // GET /api/concessions
    if (urlStr.includes('/api/concessions')) {
      return createJsonResponse(data.concessions);
    }

    // GET /api/screening/{id}/seats
    if (urlStr.match(/\/api\/screening\/\d+\/seats/)) {
      const sidMatch = urlStr.match(/\/api\/screening\/(\d+)\/seats/);
      const sid = sidMatch ? parseInt(sidMatch[1]) : 1;
      const screening = data.screenings.find(s => s.screening_id === sid) || data.screenings[0];

      // Build 30-seat auditorium grid
      const seats = [];
      const bookedIds = [3, 7, 12, 18, 19, 24]; // seeded booked seats
      const rows = ['A', 'B', 'C', 'D', 'E'];
      let seatId = 1;
      for (let r = 0; r < rows.length; r++) {
        for (let num = 1; num <= 6; num++) {
          const tier = (r === 0) ? 'Gold VIP Recliner' : ((r >= 3) ? 'Front Club' : 'Executive Prime');
          const mult = (tier.includes('VIP')) ? 1.5 : ((tier.includes('Prime')) ? 1.2 : 1.0);
          const price = Math.round(screening.ticket_price * mult);
          seats.push({
            seat_id: seatId,
            seat_number: `${rows[r]}${num}`,
            row_label: rows[r],
            seat_tier: tier,
            is_booked: bookedIds.includes(seatId),
            price: price,
            version_id: 1
          });
          seatId++;
        }
      }

      return createJsonResponse({
        screening_id: sid,
        movie_title: screening.movie_title,
        screen_number: screening.screen_number,
        screen_type: screening.screen_type,
        cinema_name: screening.cinema_name,
        show_date: screening.show_date,
        start_time: screening.start_time,
        total_capacity: seats.length,
        available_count: seats.filter(s => !s.is_booked).length,
        seats: seats
      });
    }

    // GET /api/dynamic-pricing/{screening_id}
    if (urlStr.match(/\/api\/dynamic-pricing\/\d+/)) {
      return createJsonResponse({
        screening_id: 1,
        base_price: 450,
        dynamic_ticket_price: 450.0,
        current_occupancy_pct: 78.5,
        pricing_tier: "Standard Base Rate",
        surge_multiplier: 1.0
      });
    }

    // POST /api/book-tickets
    if (urlStr.includes('/api/book-tickets') && method === 'POST') {
      const body = init.body ? JSON.parse(init.body) : {};
      const sid = body.screening_id || 1;
      const seatIds = body.seat_ids || [1, 2];
      const screening = data.screenings.find(s => s.screening_id === sid) || data.screenings[0];
      const baseTotal = seatIds.length * screening.ticket_price;
      const discount = body.promo_code ? Math.round(baseTotal * 0.20) : 0;
      const totalAmount = baseTotal - discount;
      const bookingId = Math.floor(Math.random() * 8000) + 1000;
      const txnRef = 'TXN-AURA-' + Date.now();

      const tickets = seatIds.map((sid, idx) => ({
        ticket_number: `TKT-BKG${bookingId}-S${sid}`,
        seat_id: sid,
        barcode_hash: `AURA70MM-${bookingId}-${sid}-${Date.now().toString(16)}`
      }));

      const newBooking = {
        booking_id: bookingId,
        screening_id: sid,
        movie_title: screening.movie_title,
        cinema_name: screening.cinema_name,
        screen_number: screening.screen_number,
        screen_type: screening.screen_type,
        show_date: screening.show_date,
        start_time: screening.start_time,
        seats: seatIds.map(s => `Seat #${s}`).join(', '),
        total_amount: totalAmount,
        booking_time: new Date().toISOString().replace('T', ' ').substring(0, 19),
        status: 'CONFIRMED',
        transaction_reference: txnRef,
        tickets: tickets
      };

      saveLocalBooking(newBooking);

      return createJsonResponse({
        booking_id: bookingId,
        subtotal: baseTotal,
        discount: discount,
        total_amount: totalAmount,
        transaction_reference: txnRef,
        is_idempotent_replay: false,
        tickets: tickets
      });
    }

    // GET /api/my-bookings
    if (urlStr.includes('/api/my-bookings')) {
      const local = getLocalBookings();
      const seeded = [
        {
          booking_id: 101,
          screening_id: 1,
          movie_title: "Oppenheimer",
          cinema_name: "PVR Inorbit (Cyberabad)",
          screen_number: 1,
          screen_type: "IMAX 3D Laser",
          show_date: "2026-10-04",
          start_time: "18:00",
          seats: "A3, A4",
          total_amount: 900.0,
          booking_time: "2026-10-03 14:22:00",
          status: "CONFIRMED",
          transaction_reference: "TXN-PVR-89210",
          tickets: [
            { ticket_number: "TKT-BKG101-S3", seat_number: "A3", barcode_hash: "AURA-HASH-8921-A3", status: "Active" },
            { ticket_number: "TKT-BKG101-S4", seat_number: "A4", barcode_hash: "AURA-HASH-8921-A4", status: "Active" }
          ]
        },
        {
          booking_id: 102,
          screening_id: 2,
          movie_title: "Dune: Part Two",
          cinema_name: "PVR Forum (Bengaluru)",
          screen_number: 2,
          screen_type: "4DX Dynamic Motion",
          show_date: "2026-10-05",
          start_time: "14:00",
          seats: "B5",
          total_amount: 450.0,
          booking_time: "2026-10-03 16:45:00",
          status: "CONFIRMED",
          transaction_reference: "TXN-PVR-91402",
          tickets: [
            { ticket_number: "TKT-BKG102-S5", seat_number: "B5", barcode_hash: "AURA-HASH-9140-B5", status: "Active" }
          ]
        }
      ];
      return createJsonResponse([...local, ...seeded]);
    }

    // POST /api/cancel-booking
    if (urlStr.includes('/api/cancel-booking') && method === 'POST') {
      const body = init.body ? JSON.parse(init.body) : {};
      const bkgId = body.booking_id;
      const local = getLocalBookings();
      const target = local.find(b => b.booking_id === bkgId);
      if (target) {
        target.status = 'CANCELLED';
        localStorage.setItem('aura_cinema_bookings', JSON.stringify(local));
      }
      return createJsonResponse({
        message: `Booking #${bkgId} successfully cancelled under standard 90% refund policy.`,
        booking_id: bkgId,
        original_payment: 450.0,
        cancellation_fee: 45.0,
        refund_amount: 405.0,
        refund_reference: "REF-" + Date.now(),
        policy_note: "10% administrative retention fee retained per theatre terms."
      });
    }

    // POST /api/validate-ticket
    if (urlStr.includes('/api/validate-ticket') && method === 'POST') {
      const body = init.body ? JSON.parse(init.body) : {};
      const token = (body.token || '').trim();

      if (token.includes('CANCELLED')) {
        return createJsonResponse({
          status: "DENIED",
          color: "red",
          reason: `Ticket was cancelled and refunded under 90% policy. Entry denied.`
        }, 400);
      }

      return createJsonResponse({
        status: "GRANTED",
        color: "emerald",
        message: "Welcome to AURA LUXE CINEMAS! Ticket verified successfully.",
        details: {
          ticket_number: token || "TKT-VERIFIED-01",
          barcode_hash: "SHA256-" + Date.now().toString(16),
          movie: "Oppenheimer",
          cinema: "PVR Inorbit (Cyberabad)",
          screen: 1,
          showtime: "2026-10-04 18:00"
        }
      });
    }

    // POST /api/order-concessions
    if (urlStr.includes('/api/order-concessions') && method === 'POST') {
      const body = init.body ? JSON.parse(init.body) : {};
      const orderId = Math.floor(Math.random() * 5000) + 1000;
      return createJsonResponse({
        message: "Concessions order placed successfully! Items will be delivered to your auditorium seat.",
        order_id: orderId,
        total_amount: 320.0,
        transaction_reference: "TXN-FOOD-" + Date.now()
      });
    }

    // GET /api/reports
    if (urlStr.includes('/api/reports')) {
      return createJsonResponse(data.reports);
    }

    // GET /api/status
    if (urlStr.includes('/api/status')) {
      return createJsonResponse({
        status: "ONLINE",
        engine: "SQLite 3.42.0 (SERIALIZABLE ACID Mode)",
        foreign_keys: "ENABLED",
        active_screenings: data.screenings.length,
        triggers_active: 3,
        analytical_views: 6
      });
    }

    // GET /api/schedule-timeline
    if (urlStr.includes('/api/schedule-timeline')) {
      return createJsonResponse([
        {
          screen_number: 1,
          screen_type: "IMAX 3D Laser",
          cinema: "PVR Inorbit (Cyberabad)",
          blocks: [
            { type: "Screening", title: "Oppenheimer", start: "10:00", end: "13:00", movie_id: 1 },
            { type: "Turnaround Buffer", title: "Turnaround Buffer (15 min)", start: "13:00", end: "13:15" },
            { type: "Screening", title: "Dune: Part Two", start: "14:00", end: "16:45", movie_id: 2 },
            { type: "Turnaround Buffer", title: "Turnaround Buffer (15 min)", start: "16:45", end: "17:00" }
          ]
        },
        {
          screen_number: 2,
          screen_type: "4DX Dynamic Motion",
          cinema: "PVR Inorbit (Cyberabad)",
          blocks: [
            { type: "Screening", title: "Interstellar", start: "11:00", end: "13:49", movie_id: 3 },
            { type: "Turnaround Buffer", title: "Turnaround Buffer (15 min)", start: "13:49", end: "14:04" },
            { type: "Screening", title: "Inception", start: "15:00", end: "17:28", movie_id: 5 }
          ]
        }
      ]);
    }

    // GET /api/explain-query
    if (urlStr.includes('/api/explain-query')) {
      return createJsonResponse({
        view_name: "view_show_occupancy",
        sql_query: "SELECT * FROM view_show_occupancy;",
        execution_steps: [
          { node_id: 2, detail: "SCAN sc USING COVERING INDEX idx_screenings_date", is_index_scan: true, is_b_tree_search: true, optimization_score: "High (Covering Index)" },
          { node_id: 3, detail: "SEARCH s USING INTEGER PRIMARY KEY (rowid=?)", is_index_scan: true, is_b_tree_search: true, optimization_score: "High (Covering Index)" },
          { node_id: 4, detail: "SEARCH m USING INTEGER PRIMARY KEY (rowid=?)", is_index_scan: true, is_b_tree_search: true, optimization_score: "High (Covering Index)" }
        ]
      });
    }

    // Fallback for any unhandled api call
    return createJsonResponse({ message: "OK", status: 200 });
  };
})();
