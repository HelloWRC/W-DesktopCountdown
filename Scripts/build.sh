cd `dirname $0`
source ../venv/bin/activate
python3 ./CompUI.py
pyrcc5 -o ../resources_rc.py ../resources.qrc