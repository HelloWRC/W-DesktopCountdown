@echo off
cmd /c Ready.bat

cd ..
echo ----------��������exe�ļ�----------
pyinstaller -F warp.py -p . -w -i ./resources/icons/colorful/logo.ico
cd dist
del W-DesktopCountdown*.exe
cd ..
python -c "import os;import properties;os.rename('./dist/warp.exe', './dist/W-DesktopCountdown-{}.exe'.format(properties.version_code))"
echo ----------�������----------