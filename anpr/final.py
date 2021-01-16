import cv2 as cv
import cv2
import numpy as np
import time, sys
from threading import Thread

if sys.version_info[0] == 2: # for python 2
    import Queue as queue
else:
    import queue

# for various frameworks, we just use darknet.
frameworks = ['caffe', 'tensorflow', 'torch', 'darknet', 'dldt']

# this can  adjust from callback function
confThreshold = 0.5
nmsThreshold = 0.4

# network configs
model = "./network/yolov3-tiny_obj_best.weights"
cfg = "./network/yolov3-tiny_obj.cfg"
labels = "./network/obj.names"
# variables
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

def postprocess(frame, outs):
    frameHeight, frameWidth = frame.shape[:2]
    
    def drawPred(classId, conf, left, top, right, bottom):
        # Draw a bounding box.
        cv.rectangle(frame, (left, top), (right, bottom), (0, 255, 0))

        label = '%.2f' % conf

        # Print a label of class.
        if classes:
            assert(classId < len(classes))
            label = '%s: %s' % (classes[classId], label)

        labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv.rectangle(frame, (left, top - labelSize[1]), (left + labelSize[0], top + baseLine), (255, 255, 255), cv.FILLED)
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

    layerNames = net.getLayerNames()
    lastLayerId = net.getLayerId(layerNames[-1])
    lastLayer = net.getLayer(lastLayerId)

    classIds = []
    confidences = []
    boxes = []
    if lastLayer.type == 'Region':
        # Network produces output blob with a shape NxC where N is a number of
        # detected objects and C is a number of classes + 4 where the first 4
        # numbers are [center_x, center_y, width, height]
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
        # drawPred(classIds[i], confidences[i], left, top, left + width, top + height)
        frame = frame[top:top+height ,left:left+width]


def proj(preprocessed_img):
    projs = np.sum(preprocessed_img, 1)
    m = np.max(projs)
    h, w = preprocessed_img.shape[:2]
    result = np.zeros((h,w))
    # Draw a line for each row
    for row in range(h):
        cv2.line(result, (0,row), (int(projs[row]*w/m),row), (255,255,255), 1)

    return (result, projs)
    # return projs

def proj_points(projs, ratio=5, verbose=False, bias=10):
    length_proj = len(projs)
    if True:
        # magic happened
        fs = int(bias) # first select point with bias
        fe = int (length_proj/ratio) + bias # (1 / ratio ) + bias 
        s =  int(fe + bias / 2) # (1 / ratio ) + bias + bias / 2
        e =  int(( 2 * s ) - bias) # (2 / ratio ) - bias
        if verbose : print(fs, fe, s, e)

        first_min_pt = min(projs[fs:fe])
        second_min_pt = min(projs[s:e])
        
        if verbose : print(first_min_pt, second_min_pt)
            
        first_ref_pt = np.where(projs == first_min_pt)
        second_ref_pt = np.where(projs == second_min_pt)
        
        if verbose : print(first_ref_pt, second_ref_pt)
        if len(second_ref_pt) < 3 :
            # narrow bandwidh
            second_ref_pt = list(range(second_ref_pt[0][0] - 5 , second_ref_pt[0][0] + 5 ))
    
        if len(first_ref_pt) < 3:
            # narrow bandwidh
            first_ref_pt = list(range(first_ref_pt[0][0] - 5 ,first_ref_pt[0][0] + 5 ))
    
    return (first_ref_pt,second_ref_pt)

def sort_contours(cnts,reverse = False):
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    return cnts

def find_seg(frame, kernel=(3,3)):
    blurred = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), kernel, 0)
    binary = cv2.threshold(src=blurred, thresh=125, maxval=255, type=cv2.THRESH_OTSU)[1]
    kernel5 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    dia_img = cv2.morphologyEx(binary, cv2.MORPH_DILATE, kernel5)
    cv2.imwrite('detected.jpg', dia_img)

    res ,  _ = proj(dia_img)
    cv2.imwrite('res.jpg', res)

    # first_ref_pt,second_ref_pt = proj_points(projs, ratio=5, verbose=True , bias=30)

    # upper = dia_img[first_ref_pt[0]:second_ref_pt[-1]]
    # lower = dia_img[second_ref_pt[-1]: len(projs)-15]

    # cont, _  = cv2.findContours(lower, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # digit_w, digit_h = 30, 60
    # copy_one = lower.copy()
    # crop_characters = []
    # for c in sort_contours(cont):
    #     (x, y, w, h) = cv2.boundingRect(c)
    #     ratio = h/w
    #     if 1<=ratio<=3.5: # Only select contour with defined ratio
    #         if h/lower.shape[0]>=0.5: # Select contour which has the height larger than 50% of the plate
    #             # Draw bounding box arroung digit number
    #             cv2.rectangle(copy_one, (x, y), (x + w, y + h), (0, 255,0), 2)

    #             # Sperate number and gibe prediction
    #             curr_num = dia_img[y:y+h,x:x+w]
    #             curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
    #             _, curr_num = cv2.threshold(curr_num, 220, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #             crop_characters.append(curr_num)
        
    # print("Detect {} letters...".format(len(crop_characters)))

def my_process(frame , out):
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
        find_seg(frame[top:top+height, left:left+width])
        # print('region: ' , str(top), str(top+height) , str(left), str(left+width))

# Process inputs
winName = 'Deep learning object detection in OpenCV'
cv.namedWindow(winName, cv.WINDOW_NORMAL)

def callback(pos):
    global confThreshold
    confThreshold = pos / 100.0

cv.createTrackbar('confi thrsh, %', winName, int(confThreshold * 100), 99, callback)

cap = cv.VideoCapture(0)

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

#
# Frames capturing thread
#
framesQueue = QueueFPS()
def framesThreadBody():
    global framesQueue, process

    while process:
        hasFrame, frame = cap.read()
        if not hasFrame:
            break
        framesQueue.put(frame)  # <- get frame and put to queue object

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

        my_process(frame, outs)

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
