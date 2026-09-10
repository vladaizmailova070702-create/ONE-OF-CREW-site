@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0journal.ps1" -Install
echo.
pause
