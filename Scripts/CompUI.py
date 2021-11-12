import os
import re
cwd = os.getcwd()
for f in os.listdir('../UISource'):
    #print(f)
    if re.search(r'\.ui$',f):
        #print(cwd+"/../QuickLauncher-qtremake/UIFrames/"+f[:-3])
        cmdline = 'pyuic5 -o {} {}'.format(cwd+"/../UIFrames/ui_"+f[:-3]+'.py',cwd+"/../UISource/"+f)
        print('> '+cmdline)
        os.system(cmdline)