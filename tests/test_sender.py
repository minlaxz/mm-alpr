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

while cv2.waitKey(1) < 0 :
    try:
        prev = time.time()
        ret , frame = cap.read()
        if not ret:
            print('frame is not ready')
            break
        bgr = swapRGB(frame)
        now = time.time()
        print('capturing FPS: ' , 1/ now - prev)
        repl = image_sender.send_image('rpi', bgr)
        print('sending FPS: ', 1 / time.time() - now)
        if repl == b'STOP':
            break
        else: 
            count +=1
        print('Count : ', count)
    except KeyboardInterrupt:
        break
