@echo off
title Cinema Screening and Ticket Booking System - Woxsen University
echo ======================================================================
echo   Launching Cinema Screening and Ticket Booking System (Python/SQLite)
echo ======================================================================
echo.
python "%~dp0project\app\cinema_app.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] An error occurred while launching the Python application.
    echo Please ensure Python 3 is installed and added to your system PATH.
)
echo.
pause
