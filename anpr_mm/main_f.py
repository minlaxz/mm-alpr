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
    cap.set(3, h)
    cap.set(4, w)
    log.this("waiting camera...")
    time.sleep(3)
    while (True):
        _, im = cap.read()
        resized = cv2.resize(im, (w,h) , interpolation=cv2.INTER_LINEAR)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        detections = detector.detect_image(resized_rgb=rgb)
        
        log.this("detected.") if detections else log.this("none.")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            break



if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    main(cap=cap)