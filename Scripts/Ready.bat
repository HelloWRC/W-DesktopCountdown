@echo off

echo ���ڱ���UI...
python .\CompUI.py

echo ���ڱ�����Դ�ļ�
pyrcc5 -o ..\resources_rc.py ..\resources.qrc

echo ========== �ļ�������� ==========