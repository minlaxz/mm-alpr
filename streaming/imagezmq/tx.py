"""
File - : __file__
This should be run on Client Side : Raspberry PI
"""
import os, imagezmq
from socket import gethostname as clienthostname
debug = False
server_host = '192.168.0.16'
w, h = 512, 416

sender_obj = imagezmq.ImageSender(connect_to='tcp://{}:5555'.format(server_host))
is_x64 = None
if 'arm' in os.uname()[-1]:
    from imutils.video import VideoStream
    import os, sys, traceback, time
    is_x64 = False 
else:
    import cv2
    from sys import exit
    from traceback import print_exc
    from time import sleep
    is_x64 = True
if is_x64:
    camera = cv2.VideoCapture(0)
    camera.set(3,h)
    camera.set(4,w)
else:
    camera = VideoStream(usePiCamera=True, resolution=(w,h)).start()

sleep(2.0) if is_x64 else time.sleep(2.0)
print('`{}` Camera is start.'.format(clienthostname()))
userAbord = False
try:
    while True:
        if is_x64:
            _, image = camera.read()
        else: image = camera.read()
        repl = sender_obj.send_image(clienthostname(), image)
        if (repl==b'STOP'):
            userAbord = True
            break

except (KeyboardInterrupt, SystemExit):
    print('KeyboardInterrupt')
    pass  # Ctrl-C was pressed to end program

except Exception as ex:
    print('ex')
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()

finally:
    print('User Stopped') if userAbord else print('Finally Exit')
    camera.release() if is_x64 else camera.stop()
    sender_obj.close()
    exit() if is_x64 else sys.exit()