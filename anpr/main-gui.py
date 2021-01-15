import imagezmq
import time
import cv2
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread, Event
from configs.settings import Settings
import pylaxz
import darknet


"""to handle multi thread processes."""
# class Plate:
#     def __init__(self,image_rgb):
#         self.image = image_rgb

#     def perspective(self):
#         pylaxz.printf('perspective transformation is handling.')
#         cv2.imshow('client_name', self.image)

class Application:
    def __init__(self):
        if not nodetect : self.load_detector()
        self.load_camera() if hostcamera else self.load_hub()

        # images are assigned to this
        self.array_image = None

        self.root = tk.Tk()
        self.root.title("G-22.4 ANPR TESTING") if nodetect else self.root.title('G-22.4 ANPR DETECTION')
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.panel = tk.Label(self.root)
        self.panel.pack(padx=10, pady=10)

        btn = tk.Button(self.root, text="Manual Door Command!", command=self.blackhole)
        btn.pack(fill="both", expand=True, padx=10, pady=10)

        btn = tk.Button(self.root, text="Exit!", command=self.destructor)
        btn.pack(fill="both", expand=True, padx=10, pady=10)

        self.text = tk.StringVar()
        self.label = tk.Label(self.root, textvariable=self.text)
        self.label.pack(padx=10, pady=10)

        if debug: pylaxz.printf("Everything's up", _int=1)
        self.mainLoop()
    
    def load_detector(self):
        """darknet is initialized here"""
        self.detector = darknet.LoadNetwork(networks['cfg'], networks['data'],
         networks['weight'], float(networks['thresh']), int(networks['batch_size']) )
        self.w , self.h = self.detector.network_w , self.detector.network_h

    def load_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3,640)
        self.cap.set(4,480)
        time.sleep(3.0)

    def load_hub(self):
        import imagezmq
        self.cap =imagezmq.ImageHub()

    def get_image(self):
        if hostcamera:
            _, image = self.cap.read()
            self.array_image = cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB), (self.w,self.h), interpolation=cv2.INTER_LINEAR)
        else:
            _, self.array_image = self.cap.recv_image()
    
    def get_dk_image(self):
        return darknet.make_image(self.w, self.h, 3)

    def mainLoop(self):
        self.get_image()
        if not nodetect:
            self.detections = self.detector.detect_image(self.array_image)
            if self.detections:
                if debug: pylaxz.printf('Got detections.')
                self.text.set('DETECTED by ANPR SYSTEM.')
                # print(self.detections)
                self.drawDetected()
            else: self.text.set("NOTHING.")
        else: self.text.set("NO DETECTION IS MADE.")

        #if detections:
        #    self.text.set("Detected")
        #    x = threading.Thread(target=self.thread_func, args=(1,), daemon=False)
        #    if x.is_alive():
        #        debug: pylaxz.printf('current thread is on going.')
        #    else:
        #        x.start()
        #        debug: pylaxz.printf('started another thread.')
        #    pylaxz.printf("Main : main thread done.")
        #else:
        #    self.text.set('Nothing')

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(self.array_image)) 

        self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
        self.panel.config(image=imgtk)  # show the image

        if not hostcamera: self.image_hub.send_reply(b"OK")

        self.root.after(20, self.mainLoop)  # call the same function after 30 milliseconds

    def drawDetected(self):
        left, top, right, bottom =  bbox2points(self.detections[0][2])
        self.array_image = cv2.rectangle(self.array_image, (left, top), (right, bottom), (255,0,0), 3)
        if debug: pylaxz.printf('Drawn')

    def destructor(self):
        """ Destroy the root object and release all resources """
        if hostcamera:
            self.cap.release()
            if debug: pylaxz.printf('Camera is realased.', _int=1)
        else:
            _, image = self.image_hub.recv_image()
            self.image_hub.send_reply(b"STOP")
            self.image_hub.close()

        self.root.destroy()
        pylaxz.printf('Clean up.', _int=1)
        #cv2.destroyAllWindows()  # it is not mandatory in this application

    def thread_func(self, thread_name):
        pylaxz.printf("Thread %s: starting", thread_name)
        pylaxz.printf('Door is opening.')
        self.text.set("Door is opening.")
        time.sleep(3)
        pylaxz.printf("Thread %s: finishing", thread_name)
    
    def blackhole(self): pass


def bbox2points(bbox):
    x, y, w, h = bbox
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

if __name__ == "__main__":
    s = Settings()
    networks = s.get_network
    debug, nodetect, hostcamera, gui = s.appconfigs

    app = Application() # """test=False make detections"""
    app.root.mainloop()
