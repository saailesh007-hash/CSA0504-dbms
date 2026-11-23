Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   Starting Movie Catalogue, Ratings & Revenue Dashboard (Streamlit)   " -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path $PSScriptRoot
Write-Host "Opening Streamlit on http://localhost:8501 ..." -ForegroundColor Green
Write-Host "(Keep this PowerShell window open to keep the server running)" -ForegroundColor Gray
Write-Host ""

& "C:\Users\ASUS\AppData\Local\Programs\Python\Python311\python.exe" -m streamlit run app.py --server.port 8501
