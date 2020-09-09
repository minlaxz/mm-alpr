import cv2
from settings import Settings
import g22darknet as darknet
from threading import Thread, enumerate
import time
import log
from queue import Queue

class Application:
    def __init__(self):
        app_configs = Settings()
        app_configs.read()
        self.debug = app_configs.debug
        self.use_own_camera = app_configs.localrun
        self.no_detection = app_configs.test
        if not self.no_detection : self.init_detector()
        self.setup_camera() if self.use_own_camera else self.setup_hub()

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3,640)
        self.cap.set(4,480)
        time.sleep(3.0)

    def setup_hub(self):
        import imagezmq
        self.cap =imagezmq.ImageHub()
    
    def reply(self):
        self.cap.send_reply(b"OK")

    def init_detector(self):
        self.detector = darknet.LoadNetwork(config_file, data_file, weights, thresh, batch_size)
        self.n_w = self.detector.network_w
        self.n_h = self.detector.network_h

def detect():
    while True:
        im = frame_queue.get()
        dk = dk_queue.get()
        detections = app.detector.detect_image(dk, im)
        if detections: log.this('Detected.')

def get_dk_img():
    while True:
        if dk_queue.empty():
            dk_queue.put(darknet.make_image(app.n_w, app.n_h,3))

def get_img():
    while True:
        if app.use_own_camera:
            _ , img = app.cap.read()
            img = cv2.resize(img, (app.n_w, app.n_h), interpolation=cv2.INTER_LINEAR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img = app.cap.recv_image()
            if frame_queue.empty(): app.reply()
            
        frame_queue.put(img)

if __name__ == "__main__":
    frame_queue = Queue (maxsize=1)
    dk_queue = Queue (maxsize=1)
    thresh = 0.5
    batch_size = 1
    config_file = "./network/yolov3-tiny_obj.cfg"
    data_file = "./network/obj.data"
    weights = "./network/yolov3-tiny_obj_best.weights"
    app = Application()
    t_img = Thread(target=get_img, args=())
    t_dk = Thread(target=get_dk_img, args=())
    t_detect = Thread(target=detect, args=())
    t_img.start()
    t_dk.start()
    t_detect.start()
    log.this('Network is Loaded.\nMain thread done.')