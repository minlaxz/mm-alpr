import detector as darknet
import log
import cv2
import time

thresh = 0.5
batch_size = 1
config_file = "./network/yolov3-tiny_obj.cfg"
data_file = "./network/obj.data"
weights = "./network/yolov3-tiny_obj_best.weights"

def main(cap):
    detector = darknet.LoadNetwork(config_file, data_file, weights, thresh, batch_size)
    w , h = detector.network_w , detector.network_h
    cap.set(3, 1280) # h
    cap.set(4, 480) # 480p
    log.this("Waiting camera object...")
    time.sleep(3)
    while (True):
        _, im = cap.read()
        # fps = cap.get(cv2.CAP_PROP_FPS)
        resized = cv2.resize(im, (w,h) , interpolation=cv2.INTER_LINEAR)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        detections = detector.detect_image(resized_rgb=rgb)

        # log.this("detected.") if detections else log.this("none.")
        log.this(str(cap.get(cv2.CAP_PROP_FPS)))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            log.this("exit.")
            cap.release()
            cv2.destroyAllWindows()
            break



if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    main(cap=cap)


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