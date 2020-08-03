import os, imagezmq, cv2, traceback, time, sys
from detection import darknet_video as dkv
image_hub = imagezmq.ImageHub()
dkv.initialize_darknet()
count = 0

class Plate:
    def __init__(self,image_rgb):
        self.image = image_rgb

    def perspective(self):
        print('perspective transformation is handling.')
        cv2.imshow('client_name', self.image)

try:
    while True:
        client_name, image_rgb = image_hub.recv_image()        
        # flag, image = dkv.YOLO(frame_rgb=image_rgb)
        # if flag:
        #     cv2.imshow(client_name, image)
        # else:
        #     cv2.imshow(client_name, image)
        # cv2.waitKey(1)
        # image_hub.send_reply(b"OK")
        detections = dkv.YOLO(frame_rgb=image_rgb)

        if detections:
            detected = dkv.cropDetected(detections=detections, img=cv2.resize(image_rgb,(512,416),interpolation=cv2.INTER_LINEAR))
            plate = Plate(detected)
            plate.perspective()
            #cv2.imshow(client_name, detected)
        else:
            pass
            # print(False)
            cv2.imshow(client_name, image_rgb)
        cv2.waitKey(1)

        image_hub.send_reply(b"OK")

except (KeyboardInterrupt, SystemExit):
    client_name, image = image_hub.recv_image()
    image_hub.send_reply(b'STOP')
    #pass  # Ctrl-C was pressed to end program;

except Exception as ex:
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()

finally:
    print('finally')
    cv2.destroyAllWindows()
    image_hub.close()
    sys.exit()
