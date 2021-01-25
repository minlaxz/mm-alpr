#! /bin/python3

"""
this should be run on Raspberry Pi,
no threading is including.
"""

import cv2
import imzmqx
import time

w = 512
h = 416
detection_server = '192.168.0.16'
count = 0
x = 1

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('cannot open camera.')

else:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    print('plz wait.')
    time.sleep(2.0)

connect_to = "tcp://{0}:5555".format(detection_server)
image_sender = imzmqx.ImageSender(connect_to=connect_to)   
time.sleep(1.0)

def swapRGB(bgr):
    img = cv2.resize(bgr, (w,h), interpolation=cv2.INTER_LINEAR )
    return cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

prev = time.time()

while cv2.waitKey(1) < 0 :
    try:
        count +=1
        ret , frame = cap.read()
        if not ret:
            print('frame is not ready')
            break
        bgr = swapRGB(frame)
        now = time.time()
        if (now - prev) > x:
            print('Capturing FPS: ' , count / (now - prev))
            # print('Capturing FPS: ' + str(count / (now - prev)), end="\r")
            count = 0
            prev = time.time()
        repl = image_sender.send_image('rpi', bgr)
        print('Streaming FPS: ' + str(count / (time.time() - now)))
        if repl == b'STOP':
            break
    except KeyboardInterrupt:
        break
