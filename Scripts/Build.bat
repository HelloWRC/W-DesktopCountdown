@echo off
cmd /c Ready.bat

cd ..
echo ----------正在生成exe文件----------
pyinstaller -F randomnamepicker.py -p . -i .\icons\icon.ico -w
echo ----------生成完成----------