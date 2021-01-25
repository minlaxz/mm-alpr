import imzmqx, cv2, time, queue
from threading import Thread

cap = imzmqx.ImageHub()

class QueueFPS(queue.Queue):
    def __init__(self):
        queue.Queue.__init__(self)
        self.startTime = 0
        self.counter = 0

    def put(self, v):
        queue.Queue.put(self, v)
        self.counter += 1
        if self.counter == 1:
            self.startTime = time.time()

    def getFPS(self):
        return self.counter / (time.time() - self.startTime)


process = True

framesQueue = QueueFPS()
def getImageThread():
    global framesQueue, process
    while process:
        _, frame = cap.recv_image()
        framesQueue.put(frame)
        cap.send_reply(b"OK")

    # zmq.error.ZMQError: Operation cannot be accomplished in current state
    # remove deadlocking of zmq :: 
    # dead-lock: where one is expecting the other to do a step, 
    # which will be never accomplished https://stackoverflow.com/a/41015424/10582082
    _ = cap.recv_image()
    cap.send_reply(b"STOP")

    print('getImageThread exits')


t1 = Thread(target=getImageThread)
t1.start()

while True:
    try:
        img = framesQueue.get_nowait()
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            raise SystemExit

        elif cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite('rpi-{0}.jpg'.format(time.time()),img)

        cv2.imshow("test", img)
        pylaxz.printf("fps : {}".format("%.2f" % framesQueue.getFPS()))
    except queue.Empty:
        pass

    except (KeyboardInterrupt, SystemExit):
        # cap.send_reply(b"STOP")
        pylaxz.printf("System exited.", _int=1)
        break

process = False

# main thread is waiting for t1 thread to be accomplished.
# https://stackoverflow.com/a/15086113/10582082
t1.join()

# cv2.destroyAllWindows()

