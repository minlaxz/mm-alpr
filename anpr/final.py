import cv2 as cv
import cv2
import imzmqx
import numpy as np
import time, sys
from threading import Thread
import utilsx
import pylaxz

if sys.version_info[0] == 2: # for python 2
    import Queue as queue
else:
    import queue

# for various frameworks, we just use darknet.
# frameworks = ['caffe', 'tensorflow', 'torch', 'darknet', 'dldt']

# this can  adjust from callback function
confThreshold = 0.7
nmsThreshold = 0.4

w = 512
h = 416

# network configs
model = "./network/yolov3-tiny_obj_best.weights"
cfg = "./network/yolov3-tiny_obj.cfg"
labels = "./network/obj.names"

# program variables
asyncN = 0         # wont use aysnc forward
mean = [0,0,0]     # default
scale = 1.0        # default

# Load names of classes, or just 'plate'
with open(labels, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')


# for CPU
backend = cv.dnn.DNN_BACKEND_DEFAULT
target = cv.dnn.DNN_TARGET_CPU

# for GPU
# backend = cv.dnn.DNN_BACKEND_CUDA
# target = cv.dnn.DNN_TARGET_CUDA

net = cv.dnn.readNetFromDarknet(cfg, model)
net.setPreferableBackend(backend)
net.setPreferableTarget(target)

# not detecting error
# outNames = net.getUnconnectedOutLayers()

outNames = net.getLayerNames()
outNames = [outNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

def findseg(lp_frame):

    upper_letters , lower_letters = utilsx.get_seg_char(lp_frame=lp_frame, verbose=1)


def segpostprocess(frame , out):
    frameHeight, frameWidth = frame.shape[:2]

    layerNames = net.getLayerNames()
    lastLayerId = net.getLayerId(layerNames[-1])
    lastLayer = net.getLayer(lastLayerId)

    classIds = []
    confidences = []
    boxes = []

    if lastLayer.type == 'Region':
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])
    else:
        print('Unknown output layer type: ' + lastLayer.type)
        exit()
    
    indices = np.arange(0, len(classIds))
    for i in indices:
        box = boxes[i]
        left = box[0] # x
        top = box[1] # y
        width = box[2]
        height = box[3]

        findseg(frame[top:top+height, left:left+width])

# Process inputs
winName = 'Deep learning object detection in OpenCV'
cv.namedWindow(winName, cv.WINDOW_NORMAL)

def callback(pos):
    global confThreshold
    confThreshold = pos / 100.0

cv.createTrackbar('confi thrsh, %', winName, int(confThreshold * 100), 99, callback)

def load_cam():
    cap = cv.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    pylaxz.printf('Starting up camera, plz wait...', _int=1)
    time.sleep(2.0)
    return cap

def load_hub():
    cap = imzmqx.ImageHub()
    return cap

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

cap = load_hub()
process = True

#
# Frames capturing thread
#
framesQueue = QueueFPS()
def framesThreadBody():
    global framesQueue, process

    while process:
        # hasFrame, frame = cap.read()
        # if not hasFrame:
        #     break
        _ , frame = cap.recv_image()
        framesQueue.put(frame)  # <- get frame and put to queue object
        cap.send_reply(b"OK")
    
    _  = cap.recv_image()
    cap.send_reply(b"STOP")
    print('framesThreadBody exits.')

#
# Frames processing thread
#
processedFramesQueue = queue.Queue()
predictionsQueue = QueueFPS()
def processingThreadBody():
    global processedFramesQueue, predictionsQueue, args, process

    futureOutputs = []
    while process:
        # Get a next frame
        frame = None
        try:
            frame = framesQueue.get_nowait() # <- get frame from queue object

            if asyncN:
                if len(futureOutputs) == asyncN:
                    frame = None  # Skip the frame
            else:
                framesQueue.queue.clear()  # Skip the rest of frames
        except queue.Empty:
            pass


        if not frame is None:

            inpHeight, inpWidth = frame.shape[:2]
            blob = cv.dnn.blobFromImage(frame, 1 / 255.0,  size=(inpWidth, inpHeight), swapRB=True, crop=False) # ddepth=cv.CV_8U )
            processedFramesQueue.put(frame) # <- i dont need this frame for now

            # Run a model
            net.setInput(blob, scalefactor=scale, mean=mean)

            # if net.getLayer(0).outputNameToIndex('im_info') != -1:  ## Faster-RCNN or R-FCN
            #     frame = cv.resize(frame, (inpWidth, inpHeight))
            #     net.setInput(np.array([[inpHeight, inpWidth, 1.6]], dtype=np.float32), 'im_info')

            if asyncN:
                futureOutputs.append(net.forwardAsync())
            else:
                outs = net.forward(outNames)
                predictionsQueue.put(np.copy(outs))

        while futureOutputs and futureOutputs[0].wait_for(0):
            out = futureOutputs[0].get()
            predictionsQueue.put(np.copy([out]))

            del futureOutputs[0]



framesThread = Thread(target=framesThreadBody)
framesThread.start()

processingThread = Thread(target=processingThreadBody)
processingThread.start()


while cv.waitKey(1) < 0:
    try:
        # Request prediction first because they put after frames
        outs = predictionsQueue.get_nowait()
        frame = processedFramesQueue.get_nowait()

        segpostprocess(frame, outs)

        # Put efficiency information.
        if predictionsQueue.counter > 1:
            label = 'Camera: %.2f FPS' % (framesQueue.getFPS())
            cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

            label = 'Network: %.2f FPS' % (predictionsQueue.getFPS())
            cv.putText(frame, label, (0, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

            label = 'Skipped frames: %d' % (framesQueue.counter - predictionsQueue.counter)
            cv.putText(frame, label, (0, 45), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

        cv.imshow(winName, frame)
    except queue.Empty:
        pass


process = False
framesThread.join()
processingThread.join()
