@echo off
cmd /c Ready.bat

cd ..
echo ----------��������exe�ļ�----------
pyinstaller -F warp.py -p . -w -i ./resources/icons/colorful/logo.ico
echo ----------�������----------