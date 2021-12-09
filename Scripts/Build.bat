@echo off
cmd /c Ready.bat

cd ..
echo ----------正在生成exe文件----------
pyinstaller -F warp.py -p .
echo ----------生成完成----------