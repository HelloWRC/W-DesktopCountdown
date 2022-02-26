@echo off
cmd /c Ready.bat

cd ..
echo ----------正在生成exe文件----------
pyinstaller -F warp.py -p . -w -i ./resources/icons/colorful/logo.ico
echo ----------生成完成----------