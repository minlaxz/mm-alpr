import imagezmq
import time
import cv2
import logging
from threading import Thread, enumerate

class Application:
    def __init__(self, debug=False, test=False, localrun=False):
        self.debug = debug
        if self.debug: self.config_debugger()

        self.localrun = localrun
        self.run_local() if self.localrun else self.run_hub()

        self.test = test
        if self.debug: logging.debug('detection object will be initialized.') if not self.test else logging.debug('not initialized detection object.')
        if not self.test: self.init_detection()

        self.array_image = None
        if self.debug: logging.debug('Everying up')

        if self.debug: logging.debug('Waiting...')
        self.master_loop()

    def config_debugger(self):
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")
        logging.debug('Ready.')
    
    def init_detection(self):
        """dakrnet is initialized here"""
        import detector
        self.dkv = detector
        self.dkv.initialize_darknet()
        if self.debug: logging.debug('detection object is initialized.')

    def run_local(self):
        if self.debug: logging.debug('setting camera...')
        self.image_hub = cv2.VideoCapture(0)
        self.image_hub.set(3,h)
        self.image_hub.set(4,w)
        if self.debug: logging.debug('Camera is warming up.')
        time.sleep(3.0)
        if self.debug: logging.debug('Started camera.')

    def run_hub(self):
        if self.debug: logging.debug('setting imagehub...')
        self.image_hub = imagezmq.ImageHub()
        if self.debug: logging.debug('Started imagehub server.')

    def get_image_Fhub(self):
        if self.debug: logging.debug('Getting image from imagezmq client.')
        _, self.array_image = self.image_hub.recv_image()

    def get_image_Flocal(self):
        if self.debug: logging.debug('Getting image from camera.')
        _, image = self.image_hub.read()
        self.array_image = cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),(w,h), interpolation=cv2.INTER_LINEAR)

    def master_loop(self):
        while True:
            try:
                self.get_image_Flocal() if self.localrun else self.get_image_Fhub()
                if not self.test:
                    if self.debug: logging.debug('image frame detect.')
                    self.detections = self.dkv.YOLO(self.array_image)
                    if self.detections:
                        logging.debug('Detected.')
                    else:
                        logging.debug('Nothing.')
                else:
                    if self.debug: logging.debug('image frame test.')

                if not self.localrun:
                    if self.debug: logging.debug('Reply OK')
                    self.image_hub.send_reply(b"OK")

                self.array_image = None

            except (KeyboardInterrupt, SystemExit):
                logging.debug('Keyboard is interrupted.')
                self.destructor()
                break

            except Exception as e:
                logging.debug(e)
            
    def destructor(self):
        if self.debug: logging.debug("[INFO] closing...")
        if self.localrun:
            self.image_hub.release()
            if self.debug: logging.debug('Camera is realased.')
        else:
            _, image = self.image_hub.recv_image()
            self.image_hub.send_reply(b"STOP")
            if self.debug: logging.debug('repiled STOP.')
            self.image_hub.close()
            if self.debug: logging.debug('Closed connection.')
                    
h = 416
w = 512
app = Application(debug=True, test=False, localrun=True) # """test=False make detections"""

