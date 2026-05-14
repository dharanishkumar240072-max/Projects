@echo off
echo ========================================
echo  System Resource Monitor
echo ========================================
echo.
echo Starting Flask Server...
echo Opening browser in 3 seconds...
echo.
start "" http://localhost:5000
python backend.py
pause
