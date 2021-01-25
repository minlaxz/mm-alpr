import imagezmq
import cv2

cap =imagezmq.ImageHub()

# winName = 'Deep learning object detection in OpenCV'
# cv2.namedWindow(winName, cv2.WINDOW_NORMAL)

while True:
    _ , img = cap.recv_image()
    cv2.imshow(_, img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cap.send_reply(b"STOP")
        break

    cap.send_reply(b"OK")

cv2.destroyAllWindows()

# FPS 15