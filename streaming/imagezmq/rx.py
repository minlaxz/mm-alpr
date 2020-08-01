"""
File - : __file__
This should be run on Server Side : ML Processing HOST
"""
import os, imagezmq, cv2, traceback, time, sys

image_hub = imagezmq.ImageHub()

try:
    while True:
        client_name, image = image_hub.recv_image()
        cv2.imshow(client_name, image)
        cv2.waitKey(1)
        ### everythinf goes here.
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
