import numpy as np
import cv2, time
import multiprocessing as m

# cap = cv2.VideoCapture(f'rtsp://192.168.0.146:8080/h264_pcm.sdp')

cap = cv2.VideoCapture(0)
if not cap.isOpened(): exit(1)

    
count = 0
prev = time.time()
while True:
    count += 1
    ret, frame = cap.read()
    if not ret: break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    now = time.time()
    if (now-prev) > 1 :
        # cv2.putText(gray, 'Current FPS : {}'.format(1 / (now - prev)), (5, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
        print('Avg FPS : {}'.format(count / (now - prev)))
        count = 0
        prev = time.time()

    cv2.imshow("frame", gray)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
