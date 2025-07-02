@echo off
echo ============================================
echo    Motor QR System - Excel Import Tool
echo ============================================
echo.
echo Installing required packages...
pip install pandas openpyxl
echo.
echo Starting Excel import...
python excel_import.py
echo.
echo Import process completed!
pause
