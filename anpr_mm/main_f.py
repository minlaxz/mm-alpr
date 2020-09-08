import g22darknet as darknet
import log
import cv2
import time
from threading import Thread
from queue import Queue

thresh = 0.5
batch_size = 1
config_file = "./network/yolov3-tiny_obj.cfg"
data_file = "./network/obj.data"
weights = "./network/yolov3-tiny_obj_best.weights"

def capture_video():
    while cap.isOpened():
        _ , im = cap.read()
        frame_queue.put(im)

def detect_video():
    while cap.isOpened():
        if not frame_queue.empty() : 
            prev_time = time.time()
            im = frame_queue.get() 
            resized = cv2.resize(im, (w,h) , interpolation=cv2.INTER_LINEAR)
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            print(int(1/(time.time() - prev_time)))
            
            log.this('Detected.') if detector.detect_image(rgb) else log.this('Not detected.')
            cv2.imshow('w_name', resized)

        key = cv2.waitKey(1) & 0xff

        if key == ord('q'):
            if cap.isOpened() : cap.release()
            cv2.destroyAllWindows()
            break

if __name__ == "__main__":
    frame_queue = Queue(maxsize=5)

    cap = cv2.VideoCapture(0)
    detector = darknet.LoadNetwork(config_file, data_file, weights, thresh, batch_size)
    w , h = detector.network_w , detector.network_h
    cap.set(3, 640) # h
    cap.set(4, 480) # 480p
    time.sleep(2)
    Thread(target=capture_video, args=()).start()
    Thread(target=detect_video, args=()).start()
    log.this("Main Thread Done")






























"""
def make_1080p():
    cap.set(3, 1920)
    cap.set(4, 1080)

def make_720p():
    cap.set(3, 1280)
    cap.set(4, 720)

def make_480p():
    cap.set(3, 640)
    cap.set(4, 480)

def change_res(width, height):
    cap.set(3, width)
    cap.set(4, height)

make_720p()
change_res(1280, 720)
"""