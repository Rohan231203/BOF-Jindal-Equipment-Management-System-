@echo off
echo Starting Motor QR Management System...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting the server...
echo The application will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
