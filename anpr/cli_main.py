import imagezmq
import time
import cv2
import logging
from threading import Thread, enumerate
from configparser import SafeConfigParser
from os import path

class Application:
    def __init__(self, cfgParser, cfg):
        self.cfgPath = cfg
        self.parser = cfgParser
        self.readConfig()

        if self.debug: self.configDebugger()
        self.runInLocal() if self.localrun else self.runHub()
        if self.test:
            if self.debug: logging.debug('Detection object will be BYPASS.')
        else :
            if self.debug: logging.debug('Detection object will be INITIALIZED.')
            self.initDetector()

        self.array_image = None
        if self.debug: logging.debug("Everything's up")

        self.mainLoop()

    def readConfig(self):
        self.parser.read(self.cfg_path)
        self.debug = True if (self.parser.get('cli','debug') in ['True']) else False
        self.test = True if (self.parser.get('cli','test') in ['True']) else False
        self.localrun = True if (self.parser.get('cli','localrun') in ['True']) else False
    

    def configDebugger(self):
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")
        logging.debug('Ready.')
    
    def initDetector(self):
        """dakrnet is initialized here"""
        import detector as d
        self.dkv = d
        self.dkv.initialize_darknet()
        if self.debug: logging.debug('Detection object is initialized.')

    def runInLocal(self):
        if self.debug: logging.debug('Setting camera...')
        self.capHub = cv2.VideoCapture(0)
        self.capHub.set(3,h)
        self.capHub.set(4,w)
        if self.debug: logging.debug('Camera is warming up, sleep 3.0 ...')
        time.sleep(3.0)
        logging.debug('Camera is started.')

    def runHub(self):
        if self.debug: logging.debug('Setting imagehub...')
        self.capHub = imagezmq.ImageHub()
        if self.debug: logging.debug('Started imagehub server.')

    def getImageFromHub(self):
        if self.debug: logging.debug('Getting image from imagezmq client.')
        _, self.array_image = self.capHub.recv_image()

    def getImageFromCamera(self):
        if self.debug: logging.debug('Getting image from camera.')
        _, image = self.capHub.read()
        self.array_image = cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),(w,h), interpolation=cv2.INTER_LINEAR)

    def mainLoop(self):
        while True:
            try:
                self.getImageFromCamera() if self.localrun else self.getImageFromHub()
                if not self.test:
                    if self.debug: logging.debug('detecting.')
                    self.detections = self.dkv.YOLO(self.array_image)
                    if self.detections:
                        logging.debug('Detected.')
                    else:
                        logging.debug('Nothing.')
                else:
                    if self.debug: logging.debug('bypassing.')

                if not self.localrun:
                    self.capHub.send_reply(b"OK")
                    if self.debug: logging.debug('Replied OK')

                self.array_image = None

            except (KeyboardInterrupt, SystemExit):
                logging.debug('Keyboard is interrupted.')
                self.destructor()
                break

            except Exception as e:
                logging.debug(e)
            
    def destructor(self):
        if self.debug: logging.debug("[INFO] Closing...")
        if self.localrun:
            self.capHub.release()
            if self.debug: logging.debug('Camera is realased.')
        else:
            _, image = self.capHub.recv_image()
            self.capHub.send_reply(b"STOP")
            if self.debug: logging.debug('Repiled STOP.')
            self.capHub.close()
            if self.debug: logging.debug('Closed connection.')

if __name__ == "__main__":
    h=416
    w=512
    cfgParser = SafeConfigParser()
    cfg='./anpr_mm.cfg'
    if path.exists(cfg):
        app = Application(cfgParser, cfg)
    else:
        print("CONFIG file not found.")
        exit()