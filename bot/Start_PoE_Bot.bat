@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [PoE Build Notifier] Pierwsze uruchomienie: tworzenie srodowiska Python...
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error
start "" ".venv\Scripts\pythonw.exe" "%~dp0launcher.pyw"
exit /b 0
:error
echo Nie udalo sie przygotowac bota. Sprawdz instalacje Python 3.11+.
pause
exit /b 1
