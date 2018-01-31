from __future__ import print_function
import RPi.GPIO as GPIO
import time
import os
import datetime
import urllib2
import argparse
import contextlib
import datetime
import six
import sys
import time
import unicodedata
import dropbox

'''------------------------------------------------start of uploader to dropbox------------------------------------------------'''

if sys.version.startswith('2'):
    input = raw_input  # noqa: E501,F821; pylint: disable=redefined-builtin,undefined-variable,useless-suppression

# token from tracking_2017@yahoo.com on dropbox

TOKEN = 'QetmLmriG6AAAAAAAAAAIN0XXmNSakwhOtwWtoFCZ0BytBbFz2aq-X7IcXtMA6L4'

#parser = argparse.ArgumentParser(description='Sync /usr/share/pi/dropbox-python-api/uploader to Dropbox')
parser = argparse.ArgumentParser(description='Sync /home/pi/Dropbox/camera-images to Dropbox')
#parser.add_argument('folder', nargs='?', default='uploader',help='Folder name in your Dropbox')
parser.add_argument('folder', nargs='?', default='camera-images',help='Folder name in your Dropbox')
#parser.add_argument('rootdir', nargs='?', default='/usr/share/pi/dropbox-python-api/uploader',help='Local directory to upload')
parser.add_argument('rootdir', nargs='?', default='/home/pi/Dropbox/camera-images',help='Local directory to upload')
parser.add_argument('--token', default=TOKEN, help='Access token ''(see https://www.dropbox.com/developers/apps)')
parser.add_argument('--yes', '-y', action='store_true',help='Answer yes to all questions')
parser.add_argument('--no', '-n', action='store_true',help='Answer no to all questions')
parser.add_argument('--default', '-d', action='store_true',help='Take default answer on all questions')


def internet_on():
    try:
        response=urllib2.urlopen('http://www.google.com',timeout=5)
        return True
    except urllib2.URLError as err: pass
    return False

def main():
    """Main program.
    Parse command line, then iterate over files and directories under
    rootdir and upload all files.  Skips some temporary files and
    directories, and avoids duplicate uploads by comparing size and
    mtime with the server.
    """
    args = parser.parse_args()
    if sum([bool(b) for b in (args.yes, args.no, args.default)]) > 1:
        print('At most one of --yes, --no, --default is allowed')
        sys.exit(2)
    if not args.token:
        print('--token is mandatory')
        sys.exit(2)

    folder = args.folder
    rootdir = os.path.expanduser(args.rootdir)
    print('Dropbox folder name:', folder)
    print('Local directory:', rootdir)
    if not os.path.exists(rootdir):
        print(rootdir, 'does not exist on your filesystem')
        sys.exit(1)
    elif not os.path.isdir(rootdir):
        print(rootdir, 'is not a folder on your filesystem')
        sys.exit(1)

    dbx = dropbox.Dropbox(args.token)

    #brk(host="192.168.0.179", port=9000)

    for dn, dirs, files in os.walk(rootdir):
        subfolder = dn[len(rootdir):].strip(os.path.sep)
        listing = list_folder(dbx, folder, subfolder)
        print('Descending into', subfolder, '...')

        # First do all the files.
        for name in files:
            fullname = os.path.join(dn, name)
            if not isinstance(name, six.text_type):
                name = name.decode('utf-8')
            nname = unicodedata.normalize('NFC', name)
            if name.startswith('.'):
                print('Skipping dot file:', name)
            elif name.startswith('@') or name.endswith('~'):
                print('Skipping temporary file:', name)
            elif name.endswith('.pyc') or name.endswith('.pyo'):
                print('Skipping generated file:', name)
            elif nname in listing:
                md = listing[nname]
                mtime = os.path.getmtime(fullname)
                mtime_dt = datetime.datetime(*time.gmtime(mtime)[:6])
                size = os.path.getsize(fullname)
                if (isinstance(md, dropbox.files.FileMetadata) and
                        mtime_dt == md.client_modified and size == md.size):
                    print(name, 'is already synced [stats match]')
                else:
                    print(name, 'exists with different stats, downloading')
                    res = download(dbx, folder, subfolder, name)
                    with open(fullname) as f:
                        data = f.read()
                    if res == data:
                        print(name, 'is already synced [content match]')
                    else:
                        print(name, 'has changed since last sync')
                        #if yesno('Refresh %s' % name, False, args):
                            #upload(dbx, fullname, folder, subfolder, name, overwrite=True)
                        upload(dbx, fullname, folder, subfolder, name)
            #elif yesno('Upload %s' % name, True, args):
                #upload(dbx, fullname, folder, subfolder, name)
            # upload new pictures or new files
            else:
                upload(dbx, fullname, folder, subfolder, name)

        # Then choose which subdirectories to traverse.
        keep = []
        for name in dirs:
            if name.startswith('.'):
                print('Skipping dot directory:', name)
            elif name.startswith('@') or name.endswith('~'):
                print('Skipping temporary directory:', name)
            elif name == '__pycache__':
                print('Skipping generated directory:', name)
            elif yesno('Descend into %s' % name, True, args):
                print('Keeping directory:', name)
                keep.append(name)
            else:
                print('OK, skipping directory:', name)
        dirs[:] = keep

def list_folder(dbx, folder, subfolder):
    """List a folder.
    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    path = '/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'))
    while '//' in path:
        path = path.replace('//', '/')
    path = path.rstrip('/')
    try:
        with stopwatch('list_folder'):
            res = dbx.files_list_folder(path)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', path, '-- assumed empty:', err)
        return {}
    else:
        rv = {}
        for entry in res.entries:
            rv[entry.name] = entry
        return rv

def download(dbx, folder, subfolder, name):
    """Download a file.
    Return the bytes of the file, or None if it doesn't exist.
    """
    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')
    with stopwatch('download'):
        try:
            md, res = dbx.files_download(path)
        except dropbox.exceptions.HttpError as err:
            print('*** HTTP error', err)
            return None
    data = res.content
    print(len(data), 'bytes; md:', md)
    return data

def upload(dbx, fullname, folder, subfolder, name, overwrite=False):
    """Upload a file.
    Return the request response, or None in case of error.
    """
    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')
    mode = (dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add)
    mtime = os.path.getmtime(fullname)
    with open(fullname, 'rb') as f:
        data = f.read()
    with stopwatch('upload %d bytes' % len(data)):
        try:
            res = dbx.files_upload(
                data, path, mode,
                client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                mute=True)
        except dropbox.exceptions.ApiError as err:
            print('*** API error', err)
            return None
    print('uploaded as', res.name.encode('utf8'))
    return res

def yesno(message, default, args):
    """Handy helper function to ask a yes/no question.
    Command line arguments --yes or --no force the answer;
    --default to force the default answer.
    Otherwise a blank line returns the default, and answering
    y/yes or n/no returns True or False.
    Retry on unrecognized answer.
    Special answers:
    - q or quit exits the program
    - p or pdb invokes the debugger

    """
    if args.default:
        print(message + '? [auto]', 'Y' if default else 'N')
        return default
    if args.yes:
        print(message + '? [auto] YES')
        return True
    if args.no:
        print(message + '? [auto] NO')
        return False
    if default:
        message += '? [Y/n] '
    else:
        message += '? [N/y] '
    while True:
        answer = input(message).strip().lower()
        if not answer:
            return default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        if answer in ('q', 'quit'):
            print('Exit')
            raise SystemExit(0)
        if answer in ('p', 'pdb'):
            import pdb
            pdb.set_trace()
        print('Please answer YES or NO.')

@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))

''' --------------------------------------end of uploader to dropbox-----------------------------------------------'''

''' -------------------------------------------start of recorder when montion sensed--------------------------------------------------'''

#get date and time in year-month-day-hour-minute-second format
now = datetime.datetime.now()

# assing path to the new taken picture
#OSCOMMAND = 'raspistill -o '
OSCOMMAND = 'raspistill -w 640 -h 380 -o '
PHOTOPATH = '/home/pi/Dropbox/camera-images/'
EXTENSION = '.jpg'

# process now in temp variable
temp = now.strftime("%Y-%m-%d %H:%M:%S")

# replace spaces by a minus symbol
temp = temp.replace(' ', '-')

# replace colons by a minus simbol
temp = temp.replace(':', '-')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(3, GPIO.OUT)         #LED output pin

# start streaming
# REMEMBER start sudo modprobe bcm2835-v4l2 at boot time
# by putting sudo modprobe bcm2835-v4l2 in /etc/rc.local
# BEFORE sudo service motion start
print("Starting motion")
os.system("sudo service motion start")
print("Motion started")

while True:
       i=GPIO.input(11)
       if i==0:                 #When output from motion sensor is LOW
             print ("No intruders")
             #Turn OFF LED
             GPIO.output(3, 0)
       elif i==1:               #When output from motion sensor is HIGH
             print ("Intruder detected")
             GPIO.output(3, 1)  #Turn ON LED

             #get date and time in year-month-day-hour-minute-second format
             now = datetime.datetime.now()

             # process now in temp variable
             temp = now.strftime("%Y-%m-%d %H:%M:%S")

             # replace spaces by a minus symbol
             temp = temp.replace(' ', '-')

             # replace colons by a minus simbol
             temp = temp.replace(':', '-')

             # stop streaming
             print("Stopping motion")
             os.system("sudo service motion stop")
             print("Motion stopped")

             # take picture and save it in PHOTOPATH
             print(OSCOMMAND + PHOTOPATH + temp + EXTENSION)
             os.system(OSCOMMAND + PHOTOPATH + temp + EXTENSION)

             # start streaming again
             print("Starting motion")
             os.system("sudo service motion start")
             print("Motion started")

             # start uploading to dropbox
             main()


if __name__ == '__main__':
    main()