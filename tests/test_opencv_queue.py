from queue import Queue
import cv2
import time

cap = cv2.VideoCapture(0)
q = Queue(maxsize=1)
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if q.empty(): q.put(gray)

    # Display the resulting frame
    cv2.imshow('frame',q.get())
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
