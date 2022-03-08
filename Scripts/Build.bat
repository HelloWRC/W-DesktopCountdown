@echo off
cmd /c Ready.bat

cd ..
echo ----------正在生成exe文件----------
pyinstaller -F warp.py -p . -w -i ./resources/icons/colorful/logo.ico
cd dist
move /Y warp.exe W-DesktopCountdown.exe
echo ----------生成完成----------