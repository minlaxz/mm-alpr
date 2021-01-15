import cv2
from configs.settings import Settings
import darknet
from threading import Thread
import time, pylaxz
from queue import Queue

"""
Configs = {debug},{own_camera}

"""

class Application:
    def __init__(self) -> object:
        self.load_camera() if hostcamera else self.load_hub()
        if not nodetect: self.load_detector()

    def load_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3,640)
        self.cap.set(4,480)
        time.sleep(3.0)

    def load_hub(self):
        import imagezmq
        self.cap =imagezmq.ImageHub()

    def reply(self):
        self.cap.send_reply(b"OK")

    def get_image(self):
        if hostcamera: 
            _ , img = self.cap.read()
            img = cv2.resize(img, (self.network_width, self.network_height), interpolation=cv2.INTER_LINEAR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img = self.cap.recv_image()
        return img

    def load_detector(self):
        self.detector = darknet.LoadNetwork(networks['cfg'], networks['data'],
         networks['weight'], float(networks['thresh']), int(networks['batch_size']) )

        self.network_width = self.detector.network_w
        self.network_height = self.detector.network_h

def detect():
    if debug : pylaxz.printf('detect thread started.' ,_int=1)
    while app.run:
        detections = app.detector.detect_image(q_dk_frame.get(), q_frame.get())
        try:
            if detections: pylaxz.printf(detections, _int=True) #TODO another thread or process
        except KeyboardInterrupt:
            app.run = False
            if hostcamera : app.cap.release()
            if debug : pylaxz.printf('detect thread stopped.' ,_int=1)

def get_dk_img():
    if debug : pylaxz.printf('get_dk_img thread started.' ,_int=1)
    while app.run:
        if q_dk_frame.empty():
            q_dk_frame.put(darknet.make_image(app.network_width, app.network_height,3))
        if not app.run:
            with q_dk_frame.mutex:
                q_dk_frame.queue.clear()
            if debug : pylaxz.printf('get_dk_img thread stopped.' ,_int=1)
            break

def get_img():
    if debug : pylaxz.printf('get_img thread started.' ,_int=1)
    while app.run:
        if q_frame.empty(): q_frame.put(app.get_image())
        if not hostcamera : app.reply()
        if not app.run:
            with q_frame.mutex:
                q_frame.clear()
            if debug : pylaxz.printf('get_img thread stopped.' ,_int=1)
            break

if __name__ == "__main__":
    s = Settings()
    networks = s.get_network
    debug, nodetect, hostcamera, gui = s.appconfigs

    app = Application()
    app.run = True

    q_frame = Queue(maxsize=1)
    q_dk_frame = Queue(maxsize=1)

    t_get_frame = Thread(target=get_img, args=())
    t_get_dk_frame = Thread(target=get_dk_img, args=())
    t_detect_plate = Thread(target=detect, args=())

    t_get_frame.start()
    t_get_dk_frame.start()
    t_detect_plate.start()

    pylaxz.printf('Network is Loaded.\nThree threads started.', _int=1)