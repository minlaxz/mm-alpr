import imagezmq, time
from PIL import Image, ImageTk
import tkinter as tk
from threading import Thread, Event
import cv2
import logging
from configparser import SafeConfigParser

"""to handle multi thread processes."""


# class Plate:
#     def __init__(self,image_rgb):
#         self.image = image_rgb

#     def perspective(self):
#         logging.debug('perspective transformation is handling.')
#         cv2.imshow('client_name', self.image)

class Application:
    def __init__(self, cfg_parser, cfg):
        self.cfg_path = cfg
        self.parser = cfg_parser
        self.read_config()

        if self.debug: self.config_debugger()

        if self.debug: logging.debug('detection object will be initialized.') if not self.test else logging.debug('not initialized detection object.')
        if not self.test: self.init_detection()

        self.run_local() if self.localrun else self.run_hub()

        self.array_image = None

        self.root = tk.Tk()
        self.root.title("MM ANPR TESTING") if self.test else self.root.title('MM ANPR DETECTION')
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        if self.debug: logging.debug('root is packed.')

        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)
        if self.debug: logging.debug('image panel is packed.')

        btn = tk.Button(self.root, text="Manual Door Command!", command=self.blackhole)
        btn.pack(fill="both", expand=True, padx=10, pady=10)
        if self.debug: logging.debug('door button is packed.')

        btn = tk.Button(self.root, text="Exit!", command=self.destructor)
        btn.pack(fill="both", expand=True, padx=10, pady=10)
        if self.debug: logging.debug('exit button is packed.')

        self.text = tk.StringVar()
        self.label = tk.Label(self.root, textvariable=self.text)
        self.label.pack(padx=10, pady=10)
        if self.debug: logging.debug('label is packed.')

        if self.debug: logging.debug('Everying up')

        if self.debug: logging.debug('Waiting...')
        self.master_loop()
    
    def read_config(self):
        self.parser.read(self.cfg_path)
        self.debug = bool(self.parser.get('gui', 'debug')) """used bool() to be safe."""
        self.test = bool(self.parser.get('gui', 'test'))
        self.localrun = bool(self.parser.get('gui', 'localrun'))
    
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
        self.get_image_Flocal() if self.localrun else self.get_image_Fhub()
        """ We need to process received image here """
        if not self.test:
            self.detections  = self.dkv.YOLO(self.array_image)
            if self.detections:
                if self.debug: logging.debug('Got detections.')
                self.text.set('DETECTED by ANPR SYSTEM.')
                # print(self.detections)
                self.drawDetected()
            else:
                if self.debug: logging.debug('Not detected.')
                self.text.set("NOTHING.")
        else: 
            if self.debug: logging.debug('Running test mode.')
            self.text.set("NOTHING.")

        #if detections:
        #    self.text.set("Detected")
        #    x = threading.Thread(target=self.thread_func, args=(1,), daemon=False)
        #    if x.is_alive():
        #        self.debug: logging.debug('current thread is on going.')
        #    else:
        #        x.start()
        #        self.debug: logging.debug('started another thread.')
        #    logging.debug("Main : main thread done.")
        #else:
        #    self.text.set('Nothing')

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(self.array_image)) 

        self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
        self.panel.config(image=imgtk)  # show the image

        if not self.localrun: 
            if self.debug: logging.debug('Reply OK')
            self.image_hub.send_reply(b"OK")
        self.root.after(30, self.master_loop)  # call the same function after 30 milliseconds

    def drawDetected(self):
        left, top, right, bottom =  bbox2points(self.detections[0][2])
        self.array_image = cv2.rectangle(self.array_image, (left, top), (right, bottom), (255,0,0), 3)
        if self.debug: logging.debug('Drawn')

    def destructor(self):
        """ Destroy the root object and release all resources """
        if self.debug: logging.debug("[INFO] closing...")
        if self.localrun:
            self.image_hub.release()
            if self.debug: logging.debug('Camera is realased.')
        else:
            _, image = self.image_hub.recv_image()
            self.image_hub.send_reply(b"STOP")
            if self.debug: logging.debug('Reply STOP.')
            self.image_hub.close()
            if self.debug: logging.debug('Closed connection.')

        self.root.destroy()
        if self.debug: logging.debug('Clean up.')
        #cv2.destroyAllWindows()  # it is not mandatory in this application

    def thread_func(self, thread_name):
        logging.debug("Thread %s: starting", thread_name)
        logging.debug('Door is opening.')
        self.text.set("Door is opening.")
        time.sleep(3)
        logging.debug("Thread %s: finishing", thread_name)

    def blackhole(self):
        pass

def blackhole():
    pass

def bbox2points(bbox):
    x, y, w, h = bbox
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

if __name__ == "__main__":
    h = 416
    w = 512
    cfg_parser = SafeConfigParser()
    cfg = './mm_anpr.cfg'
    app = Application(cfg_parser, cfg) # """test=False make detections"""
    app.root.mainloop()
