@echo off
cmd /c Ready.bat

cd ..
echo ---------- Building EXE ----------
pyinstaller -F warp.py -p . -w -i ./resources/icons/colorful/logo.ico
cd dist
del W-DesktopCountdown*.exe
ren ..\dist\warp.exe W-DesktopCountdown.exe
echo ---------- COMPLETED ----------