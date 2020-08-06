"""
File - : __file__
This should be run on Client Side : Raspberry PI
"""

import os, imagezmq
from socket import gethostname as name           
import cv2
import sys
import traceback
import time
import logging

class Master:
    def __init__(self, debug=False):
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO,
                            datefmt="%H:%M:%S")
        self.debug = debug
        self.is_x64 = False if 'arm' in os.name[-1] else True

        if self.debug: logging.info('`Master Constructor` : X64 device.') if self.is_x64 else logging.info('Master Constructor : X64 device.')
        self.userAbord = False
        self.count = 1
    
    def connect_server(self, server_host):
        self.server_host = server_host
        if self.debug : logging.info('`connect_server method` : Image Server is tcp/' + str(self.server_host))
        connect_to = 'tcp://{}:5555'.format(self.server_host)
        self.image_sender = imagezmq.ImageSender(connect_to=connect_to)
        if self.debug: logging.info('`connect_server method` : Connected to the server.')
    
    def send_frame(self):
        try:
            while True:
                if self.is_x64: 
                    _, image = self.camera.read()
                else: image = self.camera.read()
                resized_rgb = cv2.resize(
                            cv2.cvtColor(image, cv2.COLOR_BGR2RGB),(w,h),
                            interpolation=cv2.INTER_LINEAR)
                repl = self.image_sender.send_image(name(), resized_rgb)
                self.count += 1 
                self.debug: logging.info('`send_frame method` : {0}, {1}'. format(self.count, repl))
                if (repl==b'STOP'):
                    self.userAbord = True
                    break
        except (KeyboardInterrupt, SystemExit):
            logging.info('Keyboard is Interrupted')
            pass  # Ctrl-C was pressed to end program
        except Exception as e:
            logging.info('Python error with no Exception handler:')
            logging.info('Traceback error:', e)
            traceback.print_exc()
        finally:
            logging.info('STOP SIGNAL') if self.userAbord else logging.info('Finally Exit')
            self.camera.release() if self.is_x64 else self.camera.stop()
            if self.debug: logging.info('Released Camera Object.')
            self.image_sender.close()
            if self.debug: logging.info('Closed Connection')
            sys.exit()

    def camera_instruct(self):
        if self.debug: logging.info('`camrea_instruct method` : Creating Camera OBJECT.')
        if self.is_x64:
            self.camera = cv2.VideoCapture(0)
            self.camera.set(3,h)
            self.camera.set(4,w)
        else:
            from imutils import VideoStream
            self.camera = VideoStream(usePiCamera=True, resolution=(w,h)).start()
        if self.debug: logging.info('`camera_instruct method` : Camera is warming up.')
        time.sleep(2.0)
        logging.info('`camera_instruct method` : `{}` Camera is start.'.format(name()))

debug = True
w, h = 512, 416
app = Master(debug=debug)
if debug: logging.info('`Main Thread` : Image Sender is initialized.')
app.camera_instruct()
app.connect_server('localhost')
app.send_frame()

