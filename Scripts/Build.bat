@echo off
cmd /c Ready.bat

cd ..
echo ----------正在生成exe文件----------
pyinstaller -F warp.py -p . -w -i ./resources/icons/colorful/logo.ico
cd dist
del W-DesktopCountdown*.exe
cd ..
python -c "import os;import properties;os.rename('./dist/warp.exe', './dist/W-DesktopCountdown-{}.exe'.format(properties.version_code))"
echo ----------生成完成----------