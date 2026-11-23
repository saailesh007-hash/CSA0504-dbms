@echo off
title Movie Analytics Dashboard - Streamlit Server
color 0A
echo ======================================================================
echo    Starting Movie Catalogue, Ratings & Revenue Dashboard (Streamlit)
echo ======================================================================
echo.
cd /d "%~dp0"
echo Working Directory: %CD%
echo Starting Streamlit server on http://localhost:8501 ...
echo (Keep this window open while using the dashboard in your browser)
echo.

"C:\Users\ASUS\AppData\Local\Programs\Python\Python311\python.exe" -m streamlit run app.py --server.port 8501

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Streamlit exited with error code %ERRORLEVEL%.
    pause
)
