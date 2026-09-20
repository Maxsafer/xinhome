@echo off
setlocal

REM Builds dist\xinhome\xinhome.exe (no console window) with PyInstaller.
REM --onedir on purpose: a --onefile exe unpacks itself on every launch (~1.7 s slower per press).
cd /d "%~dp0"

python -m PyInstaller --onedir --noconsole --noconfirm --name xinhome ^
  --distpath dist --workpath build --specpath build ^
  --add-binary "%~dp0vgamepad\win\vigem\client\x64\ViGEmClient.dll;vgamepad/win/vigem/client/x64" ^
  xinhome.py

if %ERRORLEVEL% NEQ 0 (
  echo [error] Build failed. Is PyInstaller installed?  pip install pyinstaller
  pause
)
endlocal
