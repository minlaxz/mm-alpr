import imagezmq
import time
import cv2
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread, Event
import log
from settings import Settings

"""to handle multi thread processes."""
# class Plate:
#     def __init__(self,image_rgb):
#         self.image = image_rgb

#     def perspective(self):
#         log.this('perspective transformation is handling.')
#         cv2.imshow('client_name', self.image)

class Application:
    def __init__(self):
        configs = Settings()
        configs.read()
        self.debug = configs.debug
        self.localrun = configs.localrun
        self.test = configs.test
        self.gui = configs.gui #TODO

        self.onOwnCamera() if self.localrun else self.onHub()
        log.this("Detector will not be initialized.") if self.test else self.initDetector()

        self.array_image = None

        self.root = tk.Tk()
        self.root.title("G-22.4 ANPR TESTING") if self.test else self.root.title('G-22.4 ANPR DETECTION')
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        if self.debug: log.this('root is packed.')

        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)
        if self.debug: log.this('image panel is packed.')

        btn = tk.Button(self.root, text="Manual Door Command!", command=self.blackhole)
        btn.pack(fill="both", expand=True, padx=10, pady=10)
        if self.debug: log.this('door button is packed.')

        btn = tk.Button(self.root, text="Exit!", command=self.destructor)
        btn.pack(fill="both", expand=True, padx=10, pady=10)
        if self.debug: log.this('exit button is packed.')

        self.text = tk.StringVar()
        self.label = tk.Label(self.root, textvariable=self.text)
        self.label.pack(padx=10, pady=10)
        if self.debug: log.this('label is packed.')

        if self.debug: log.this("Everything's up")
        self.mainLoop()
    
    def initDetector(self):
        """darknet is initialized here"""
        import g22darknet as darknet
        self.detector = darknet.LoadNetwork(config_file, data_file, weights, thresh, batch_size)
        self.w , self.h = self.detector.network_w , self.detector.network_h
        log.this('detection object is initialized.')

    def onOwnCamera(self):
        if self.debug: log.this('setting camera...')
        self.image_hub = cv2.VideoCapture(0)
        self.image_hub.set(3,640)
        self.image_hub.set(4,480)
        if self.debug: log.this('Camera is warming up.')
        time.sleep(3.0)
        if self.debug: log.this('Started camera.')

    def onHub(self):
        if self.debug: log.this('setting imagehub...')
        self.image_hub = imagezmq.ImageHub()
        if self.debug: log.this('Started imagehub server.')

    def getImageFromHub(self):
        if self.debug: log.this('Getting image from imagezmq client.')
        _, self.array_image = self.image_hub.recv_image()

    def getImageFromCamera(self):
        if self.debug: log.this('Getting image from camera.')
        _, image = self.image_hub.read()
        self.array_image = cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB), (self.w,self.h), interpolation=cv2.INTER_LINEAR)

    def mainLoop(self):
        self.getImageFromCamera() if self.localrun else self.getImageFromHub()
        """ We need to process received image here """
        if not self.test:
            # self.detections  = self.dkv.YOLO(self.array_image)
            self.detections = self.detector.detect_image(self.array_image)
            if self.detections:
                if self.debug: log.this('Got detections.')
                self.text.set('DETECTED by ANPR SYSTEM.')
                # print(self.detections)
                self.drawDetected()
            else: self.text.set("NOTHING.")
        else: self.text.set("NOTHING.")

        #if detections:
        #    self.text.set("Detected")
        #    x = threading.Thread(target=self.thread_func, args=(1,), daemon=False)
        #    if x.is_alive():
        #        self.debug: log.this('current thread is on going.')
        #    else:
        #        x.start()
        #        self.debug: log.this('started another thread.')
        #    log.this("Main : main thread done.")
        #else:
        #    self.text.set('Nothing')

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(self.array_image)) 

        self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
        self.panel.config(image=imgtk)  # show the image

        if not self.localrun: 
            if self.debug: log.this('Reply OK')
            self.image_hub.send_reply(b"OK")
        self.root.after(30, self.mainLoop)  # call the same function after 30 milliseconds

    def drawDetected(self):
        left, top, right, bottom =  bbox2points(self.detections[0][2])
        self.array_image = cv2.rectangle(self.array_image, (left, top), (right, bottom), (255,0,0), 3)
        if self.debug: log.this('Drawn')

    def destructor(self):
        """ Destroy the root object and release all resources """
        if self.debug: log.this("[INFO] closing...")
        if self.localrun:
            self.image_hub.release()
            if self.debug: log.this('Camera is realased.')
        else:
            _, image = self.image_hub.recv_image()
            self.image_hub.send_reply(b"STOP")
            if self.debug: log.this('Reply STOP.')
            self.image_hub.close()
            if self.debug: log.this('Closed connection.')

        self.root.destroy()
        log.this('Clean up.')
        #cv2.destroyAllWindows()  # it is not mandatory in this application

    def thread_func(self, thread_name):
        log.this("Thread %s: starting", thread_name)
        log.this('Door is opening.')
        self.text.set("Door is opening.")
        time.sleep(3)
        log.this("Thread %s: finishing", thread_name)

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
    thresh = 0.5
    batch_size = 1
    config_file = "./network/yolov3-tiny_obj.cfg"
    data_file = "./network/obj.data"
    weights = "./network/yolov3-tiny_obj_best.weights"
    app = Application() # """test=False make detections"""
    app.root.mainloop()
