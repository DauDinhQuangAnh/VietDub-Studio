# Script khoi dong VietDub Studio che do Local / May Dev khong GPU
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   🎬 VIETDUB STUDIO - LOCAL DEVELOPMENT RUNNER" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Tim Python
$python = "D:\hoctap\python\python.exe"
if (-not (Test-Path $python)) {
    $python = (Get-Command "python.exe" -ErrorAction SilentlyContinue).Source
}
if (-not $python -or -not (Test-Path $python)) {
    Write-Error "Khong tim thay Python. Vui long cai dat Python hoac kiem tra duong dan."
    exit 1
}
Write-Host "[1/4] Python duoc su dung: $python" -ForegroundColor Green

# 2. File .env
if (-not (Test-Path (Join-Path $Root ".env"))) {
    Write-Host "[2/4] Khoi tao file .env tu .env.example..." -ForegroundColor Yellow
    Copy-Item (Join-Path $Root ".env.example") (Join-Path $Root ".env")
} else {
    Write-Host "[2/4] File .env da san sang." -ForegroundColor Green
}

# 3. Kiem tra FFmpeg
$ffmpegFound = $false
if (Get-Command "ffmpeg" -ErrorAction SilentlyContinue) {
    $ffmpegFound = $true
} elseif (Test-Path (Join-Path $Root "tools\ffmpeg\bin\ffmpeg.exe")) {
    $ffmpegFound = $true
    $env:PATH = "$(Join-Path $Root 'tools\ffmpeg\bin');$env:PATH"
}
if ($ffmpegFound) {
    Write-Host "[3/4] FFmpeg da san sang trong PATH." -ForegroundColor Green
} else {
    Write-Host "[3/4] CHU Y: FFmpeg chua co trong PATH. Ban co the cai dat qua: winget install Gyan.FFmpeg" -ForegroundColor Yellow
}

# 4. Frontend npm
$npm = (Get-Command "npm.cmd" -ErrorAction SilentlyContinue).Source
if (-not $npm) {
    Write-Error "Khong tim thay Node.js / npm.cmd tren may."
    exit 1
}
$webDir = Join-Path $Root "web"
if (-not (Test-Path (Join-Path $webDir "node_modules"))) {
    Write-Host "Dang cai dat dependencies web (npm install)..." -ForegroundColor Yellow
    Set-Location $webDir
    & $npm install
    Set-Location $Root
}

Write-Host "`nDang khoi dong cac tien trinh nen..." -ForegroundColor Cyan

# Khoi dong Celery Worker
$celeryCmd = "cd '$Root'; & '$python' -m celery -A worker.jobs.celery_app worker --loglevel=info --pool=solo"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$celeryCmd" -WindowStyle Minimized
Write-Host "✓ Celery Worker da khoi dong." -ForegroundColor Green

# Khoi dong FastAPI Backend
$apiCmd = "cd '$Root'; & '$python' -m uvicorn api.main:app --host localhost --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$apiCmd" -WindowStyle Minimized
Write-Host "✓ FastAPI Backend da khoi dong (http://localhost:8000)." -ForegroundColor Green

# Khoi dong Frontend Vite Dev
$webCmd = "cd '$webDir'; & '$npm' run dev -- --host localhost --port 5173"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$webCmd" -WindowStyle Minimized
Write-Host "✓ Vite Frontend da khoi dong (http://localhost:5173)." -ForegroundColor Green

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "   🚀 VIETDUB STUDIO DA KHOI DONG THANH CONG!" -ForegroundColor Green
Write-Host "   🌐 Truyen cap ngay: http://localhost:5173" -ForegroundColor Yellow
Write-Host "   (Khong can dang nhap, vao thang Studio lam viec)" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan

Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"
