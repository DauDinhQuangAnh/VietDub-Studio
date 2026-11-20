@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_project.ps1"
if errorlevel 1 (
    echo.
    echo Start Project failed. Read the message above, then press any key to close.
    pause >nul
)
