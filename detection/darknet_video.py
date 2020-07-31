import os
import cv2
import time
import darknetanpr as darknet
import imutils, imagezmq
def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def cropDetected(detections, img):
    for d in detections:
        xmin, ymin, xmax, ymax = convertBack(float(d[2][0]), float(d[2][1]), float(d[2][2]), float(d[2][3]))
        return img[ymin:ymax, xmin:xmax] if detections else None

netMain = None
metaMain = None
altNames = None

def YOLO():

    global metaMain, netMain, altNames
    configPath = "./network/yolov3-tiny_obj.cfg"
    weightPath = "./network/yolov3-tiny_obj_best.weights"
    metaPath = "./network/obj.data"
    if not os.path.exists(configPath):
        raise ValueError("Invalid config path `" +
                         os.path.abspath(configPath)+"`")
    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `" +
                         os.path.abspath(weightPath)+"`")
    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `" +
                         os.path.abspath(metaPath)+"`")
    if netMain is None:
        netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
    if metaMain is None:
        metaMain = darknet.load_meta(metaPath.encode("ascii"))
    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents,
                                  re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass

    # cap = cv2.VideoCapture('rtsp://user:userpassword@192.168.0.16:8554/live.sdp')
    # cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
    
    # cap = cv2.VideoCapture(0)
    # cap.set(3, darknet.network_height(netMain))
    # cap.set(4, darknet.network_width(netMain))
    
    # out = cv2.VideoWriter(
    #    "output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 10.0,
    #    (darknet.network_width(netMain), darknet.network_height(netMain)))
    
    imageHub = imagezmq.ImageHub()
    print("Starting the YOLO loop...")

    # Create an image we reuse for each detect
    darknet_image = darknet.make_image(darknet.network_width(netMain),
                                    darknet.network_height(netMain),3)
    count = 0
    while True:
        #print('fps: ',str(cap.get(cv2.CAP_PROP_FPS)))
        prev_time = time.time()
        #_, frame_read = cap.read()
        _, frame_read = imageHub.recv_image()
        imageHub.send_reply(b'OK')
        frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb,
                                   (darknet.network_width(netMain),
                                    darknet.network_height(netMain)),
                                   interpolation=cv2.INTER_LINEAR) # image is already resized by sender (client) (512, 416)

        darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())

        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.75)

        # image = cvDrawBoxes(detections, frame_resized)
        if detections:
            if detections[0][1] > 0.95:
                count += 1
                print(count)
                if count == 20:
                    image = cropDetected(detections, frame_resized)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    #cv2.imwrite('image.jpg', image)
                    print(detections[0][1])
                    return image            ## This will handle by @Katsura \
                    # you will need to call this module's YOLO() without any args. \
                    # grab something like image  = YOLO()
                    break
                else: pass
            else: count = count - 3 #rarely 
        else: count = 0


        # print('time',1/(time.time()-prev_time))
        # if (detections == []) :
        #     pass
        # else:
        #     print("class : ", str(detections[0][0]))
        #     print("x y w h : " , str(detections[0][2]))
        
        # cv2.imshow(Name, image)
        # if cv2.waitKey(10) & 0xFF == ord('q'):
        #     break
    # we do not need to release anything
    # cap.release()
    # out.release()

# if __name__ == "__main__":
#     YOLO()
