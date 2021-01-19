"""
File - : __file__
This should be run on Client Side : Raspberry PI or like Low Power PC

Example:
    app = Sender()
    app.run()
"""

from threading import Thread
import time, imzmqx, traceback
from socket import gethostname
import cv2, queue
import pylaxz

w = 512
h = 416

count = 0
swap_rgb = False

prev = 0
now = 0


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    pylaxz.printf('Cannot open camera.', _int=1)    
    exit()
else:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    pylaxz.printf('Starting up camera, plz wait...', _int=1)
    time.sleep(2.0)

connect_to = "tcp://{}:5555".format('localhost')
image_sender = imzmqx.ImageSender(connect_to=connect_to)   
time.sleep(1.0)

class QueueFPS(queue.Queue):
    def __init__(self):
        queue.Queue.__init__(self)
        self.now = time.time()
        self.prev = 0
        self.counter = 0

    def put(self, v):
        queue.Queue.put(self, v)
        self.counter += 1

    def getFPS(self):
        return '%.2f' % (self.counter / (time.time() - self.now))
        # print(self.now)
        # fps = '%.2f' % (1 / (self.now - self.prev))
        # self.prev = self.now
        # return fps

process = True

#
# frame capturing thread
#
frameQueue = QueueFPS()
def frameGetThread():
    global frameQueue
    while process:
        # ret , img = cap.read()
        name , img = 
        if not ret:
            pylaxz.printf('frame is not ready', _int=1, _shell=1)
            break
        frameQueue.put(img)
    print('frameGetThread exits')

#
# preprocessed thread
#
# processedQueue = queue.Queue()
processedQueue = QueueFPS()
def processThread():
    global processedQueue
    while process:
        frame = None
        try:
            frame = frameQueue.get_nowait()
            if not frame is None:
                img = cv2.resize(frame, (w,h), interpolation=cv2.INTER_LINEAR)
                processedQueue.put(cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if swap_rgb else img)
        except queue.Empty:
            pass
        except Exception as e:
            print(e)
    print('processThread exits')

        # except queue.Empty:
        #     pass

frameThread = Thread(target=frameGetThread)
frameThread.start()

processThread = Thread(target=processThread)
processThread.start()

while cv2.waitKey(1) < 0:
    try:
        frame = processedQueue.get_nowait()
        repl = image_sender.send_image(gethostname(), frame)
        if repl == b'STOP':
            raise SystemExit
        else: 
            count += 1
        print('capturing fps: {}\npreprocessed fps: {}\ncount: {}'.format(frameQueue.getFPS(), processedQueue.getFPS(), count))
    
    except queue.Empty:
        pass

    except (KeyboardInterrupt,SystemExit):
        pylaxz.printf('System exited.', _int=1)
        break # idk process has to be killed with force

process = False
frameThread.join()
processThread.join()
if cap.isOpened():
    cap.release()
    print('Camera is Released.')

exit()
# fps = '%.2f' % (1 / (now - prev))