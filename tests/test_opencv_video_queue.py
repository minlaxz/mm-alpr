import multiprocessing
import cv2, time

_PROCESS = True
cap = cv2.VideoCapture(0)
time.sleep(2.0)


def cam_loop(framesQueue):
    global _PROCESS
    
    while _PROCESS:
        _, img = cap.read()
        if _ : framesQueue.put(img)
 
    print('cam_loop exits.')


logger = multiprocessing.log_to_stderr()
logger.setLevel(multiprocessing.SUBDEBUG)
framesQueue = multiprocessing.Queue()
cam_process = multiprocessing.Process(target=cam_loop, args=(framesQueue,))
cam_process.start()

while cv2.waitKey(1) < 0:
    if not framesQueue.empty():
        out = framesQueue.get()
        cv2.imshow('ok',out)
_PROCESS = False
cap.release()
cam_process.terminate()
cam_process.join()
print("MAIN END.")

