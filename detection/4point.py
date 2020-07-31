import darknet_video as detector
import cv2

gray_image = detector.YOLO()
blur = cv2.GaussianBlur(src=gray_image, ksize=(3,3), sigmaX=0)
T,thresh_image_blured = cv2.threshold(src=blur,thresh=0, maxval=255, type=cv2.THRESH_OTSU)
edged = cv2.Canny(thresh_image_blured, 30, 200)

cv2.imwrite('image.jpg', edged)
