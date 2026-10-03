#!/bin/bash
echo "======================================================================"
echo "  Launching Cinema Screening and Ticket Booking System (Python/SQLite)"
echo "======================================================================"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python3 "$DIR/project/app/cinema_app.py"
