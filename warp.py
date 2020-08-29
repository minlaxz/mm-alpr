import numpy as np
import cv2
import matplotlib.pyplot as plt
import imutils

    def main():
        image = how to set image path :3
        image = cv2.imread(image)
        ratio = image.shape[0] / 300.0
        image = imutils.resize(image, height = 300)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(src=gray, ksize=(3,3), sigmaX=0)
        T,thresh_image_blured = cv2.threshold(src=blur,thresh=0, maxval=255, type=cv2.THRESH_OTSU)
        edged = cv2.Canny(thresh_image_blured, 30, 200)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
        screenCnt = None
        for c in cnts:
	        peri = cv2.arcLength(c, True)
	        approx = cv2.approxPolyDP(c, 0.015 * peri, True)
                if len(approx) == 4:
		        screenCnt = approx
		        break
        pts = screenCnt.reshape(4, 2)
        rect = np.zeros((4, 2), dtype = "float32")
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        rect *= ratio
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))
        dst = np.array([
	        [0, 0],
	        [maxWidth - 1, 0],
	        [maxWidth - 1, maxHeight - 1],
	        [0, maxHeight - 1]], dtype = "float32")
        M = cv2.getPerspectiveTransform(rect, dst)
        warp = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))
        warp = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
        (h, w) = warp.shape
        (dX, dY) = (int(w * 0.4), int(h * 0.45))
        crop = warp[10:dY, w - dX:w - 10]
        cv2.imwrite("warped.png", warp)
        cv2.waitKey(0)

    if __name__ == "__main__":
        main()