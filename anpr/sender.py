"""
File - : __file__
This should be run on Client Side : Raspberry PI or PC like x64
Adapted with Windows OS
"""

import os
from socket import gethostname
import cv2
import traceback
import time
import logxs as log
import imzmqx

class Master:
    def __init__(self, debug=False, test=False, server=None):
        self.debug = debug
        self.test = test
        self.server_host = server if server else 'localhost'
        self.is_posix = True if os.name is 'posix' else False
        self.userAbord = False
        self.count = 1

        # format = "%(asctime)s: %(message)s"
        # logging.basicConfig(format=format, level=log.this, datefmt="%H:%M:%S")
        
        if self.debug: log.this('platform : posix .') if self.is_posix else log.this('platform : nt .')
        log.this('Ready.')
    
    def run(self):
        self.camera_instruct()
        log.this('`camera_instruct` : `{}` Camera is start.'.format(name()))
        self.connect_server()
        if self.debug: log.this('Connected to the server.')
        self.send_frame()
    
    def connect_server(self):
        if self.debug : log.this('Server is tcp/' + str(self.server_host))
        connect_to = 'tcp://{}:5555'.format(self.server_host)
        self.image_sender = imzmqx.ImageSender(connect_to=connect_to)
        if self.debug: log.this('Image sender is inittialized.')

    
    def send_frame(self):
        if self.debug: log.this('Handling over frame sending method.')
        try:
            while True:
                _ , image = self.camera.read()

                resized_rgb = image if self.test else cv2.resize( cv2.cvtColor(image, cv2.COLOR_BGR2RGB),(w,h),
                                                                interpolation=cv2.INTER_LINEAR)

                repl = self.image_sender.send_image( gethostname() , resized_rgb)
                self.count += 1 
                if self.debug: log.this('`send_frame method` : {0}, {1}'. format(self.count, repl))
                if (repl==b'STOP'):
                    self.userAbord = True
                    break
        except (KeyboardInterrupt, SystemExit):
            log.this('Keyboard is Interrupted')
            pass  # Ctrl-C was pressed to end program
        except Exception as e:
            log.this('error with no Exception handler:')
            log.this('Traceback error:', e)
            traceback.print_exc()
        finally:
            log.this('got STOP SIGNAL') if self.userAbord else log.this('Finally Exit')
            self.camera.release()
            if self.debug: log.this('Released Camera Object.')
            self.image_sender.close()
            if self.debug: log.this('Closed Connection')
            log.this('Done.')

    def camera_instruct(self):
        if self.debug: log.this('Creating Camera OBJECT.')
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3,h)
        self.camera.set(4,w)
        if self.debug: log.this('set frame dimention: w{},h{}'.format(w,h))
        log.this('Camera is warming up.')
        time.sleep(3.0)

w, h = 512, 416
app = Master(debug=True, test=False, server='192.168.0.16')
app.run()
