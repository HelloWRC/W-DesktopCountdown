@echo off

echo 正在编译UI...
python .\CompUI.py

echo 正在编译资源文件
pyrcc5 -o ..\resources_rc.py ..\resources.qrc

echo ========== 文件编译完成 ==========