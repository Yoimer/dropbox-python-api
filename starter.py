'''
this script starts at boot time on crontab
it keeps running SCRIPT code even when
unstable internet connection makes SCRIPT crash
this is a bug fix for that trouble
'''

import os

'''
path where script resides,
including its python2 invocation
'''
PATH = 'python /usr/share/pi/dropbox-python-api/'

'''script name'''
SCRIPT = 'updown.py'

'''
infinite monitoring
'''
while True:
    os.system(PATH + SCRIPT)