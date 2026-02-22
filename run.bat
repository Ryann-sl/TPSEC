@echo off
echo Starting Cyber Security Learning Platform...
echo.

call venv\Scripts\activate.bat

echo Server starting at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python backend\app.py
