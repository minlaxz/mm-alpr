import imagezmq, time
from PIL import Image, ImageTk
import tkinter as tk
from threading import Thread, Event
import cv2

"""to handle multi thread processes."""


# class Plate:
#     def __init__(self,image_rgb):
#         self.image = image_rgb

#     def perspective(self):
#         print('perspective transformation is handling.')
#         cv2.imshow('client_name', self.image)

class Application:
    def __init__(self, debug=False, test=False, localrun=False):

        self.debug = debug
        self.test = test
        self.localrun = localrun

        if not self.test: self.init_detection()
        self.run_local() if self.localrun else self.run_hub()

        self.array_image = None

        self.root = tk.Tk()
        self.root.title("MM ANPR TESTING") if self.test else self.root.title('MM ANPR DETECTION')
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
        self.master_loop()
    
    def init_detection(self):
        """dakrnet is initialized here"""
        import detector
        self.dkv = detector
        self.dkv.initialize_darknet()

    def run_local(self):
        self.image_hub = cv2.VideoCapture(0)
        self.image_hub.set(3,h)
        self.image_hub.set(4,w)
        time.sleep(3.0)

    def run_hub(self):
        self.image_hub = imagezmq.ImageHub()

    def get_image_Fhub(self):
        _, self.array_image = self.image_hub.recv_image()

    def get_image_Flocal(self):
        _, image = self.image_hub.read()
        self.array_image = cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),(w,h), interpolation=cv2.INTER_LINEAR)

    def master_loop(self):
        self.get_image_Flocal() if self.localrun else self.get_image_Fhub()
        """ We need to process received image here """
        if not self.test:
            self.detections  = self.dkv.YOLO(self.array_image)
            if self.detections:
                self.text.set('DETECTED by ANPR SYSTEM.')
                # print(self.detections)
                self.drawDetected()
            else:
                self.text.set("NOTHING.")
        else: self.text.set("NOTHING.")

        #if detections:
        #    self.text.set("Detected")
        #    x = threading.Thread(target=self.thread_func, args=(1,), daemon=False)
        #    if x.is_alive():
        #        self.debug: print('current thread is on going.')
        #    else:
        #        x.start()
        #        self.debug: print('started another thread.')
        #    print("Main : main thread done.")
        #else:
        #    self.text.set('Nothing')

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(self.array_image)) 

        self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
        self.panel.config(image=imgtk)  # show the image

        if not self.localrun: self.image_hub.send_reply(b"OK")
        self.root.after(30, self.master_loop)  # call the same function after 30 milliseconds

    def drawDetected(self):
        left, top, right, bottom =  bbox2points(self.detections[0][2])
        self.array_image = cv2.rectangle(self.array_image, (left, top), (right, bottom), (255,0,0), 3)

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        if self.localrun:
            self.image_hub.release()
        else:
            _, image = self.image_hub.recv_image()
            self.image_hub.send_reply(b"STOP")
            self.image_hub.close()

        self.root.destroy()
        #cv2.destroyAllWindows()  # it is not mandatory in this application

    def thread_func(self, thread_name):
        print("Thread %s: starting", thread_name)
        print('Door is opening.')
        self.text.set("Door is opening.")
        time.sleep(3)
        print("Thread %s: finishing", thread_name)

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
h = 416
w = 512
app = Application(debug=True, test=False, localrun=True) # """test=False make detections"""
app.root.mainloop()
