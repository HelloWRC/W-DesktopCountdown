@echo off
cmd /c Ready.bat

cd ..
echo ----------��������exe�ļ�----------
pyinstaller -F randomnamepicker.py -p . -i .\icons\icon.ico -w
echo ----------�������----------