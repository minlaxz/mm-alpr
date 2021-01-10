#!$HOME/miniconda3/envs/ml/bin/python
"""
@author: Philip Kahn
@date: 20180503
@forkFrom: https://github.com/AlexeyAB/darknet/blob/master/darknet.py
@CAPI: https://github.com/AlexeyAB/darknet/blob/master/include/darknet.h
@authorOfYolo: https://pjreddie.com/darknet
# adaptedProject: (TTU-2019-2020-EC)-Final Year Project-Group-22
# https://github.com/minlaxz/darkent-thesisz
# Adapted with ImageZMQ
# This must be supplied resized RGB frame and return detected image if detection else None
"""
from ctypes import *
import os
import random
import math

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int),
                ("uc", POINTER(c_float)),
                ("points", c_int),
                ("embeddings", POINTER(c_float)),
                ("embedding_size", c_int),
                ("sim", c_float),
                ("track_id", c_int)]

class DETNUMPAIR(Structure):
    _fields_ = [("num", c_int),
                ("dets", POINTER(DETECTION))]

class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

def class_colors(names):
    """
    Create a dict with one random BGR color for each
    class name
    """
    return {name: (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)) for name in names}

def decode_detection(detections):
    decoded = []
    for label, confidence, bbox in detections:
        confidence = str(round(confidence * 100, 2))
        decoded.append((str(label), confidence, bbox))
    return decoded


def remove_negatives(detections, class_names, num):
    """
    Remove all classes with 0% confidence within the detection
    """
    predictions = []
    for j in range(num):
        for idx, name in enumerate(class_names):
            if detections[j].prob[idx] > 0:
                bbox = detections[j].bbox
                bbox = (bbox.x, bbox.y, bbox.w, bbox.h)
                predictions.append((name, detections[j].prob[idx], (bbox)))
    return predictions

class NetworkParameters:
    def __init__(self, _config, _data, _weights, _thresh):
        self.config_file = _config
        self.data_file = _data
        self.weights = _weights
        self.thresh  = _thresh

    def check_arguments_errors(self):
        assert 0 < self.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
        if not os.path.exists(self.config_file):
            raise(ValueError("Invalid config path {}".format(os.path.abspath(args.config_file))))
        if not os.path.exists(self.weights):
            raise(ValueError("Invalid weight path {}".format(os.path.abspath(args.weights))))
        if not os.path.exists(self.data_file):
            raise(ValueError("Invalid data file path {}".format(os.path.abspath(args.data_file))))

class LoadNetwork(NetworkParameters):
    def __init__(self, config_file, data_file, weights, thresh=0.5 , batch_size=1):
        super().__init__(config_file, data_file, weights, thresh)
        self.check_arguments_errors()
        
        self.hier_thresh = .5
        self.nms = .45
        self.thresh = thresh

        debug = False
        
        self.network = load_net_custom(
            self.config_file.encode("ascii"),
            self.weights.encode("ascii"), 0, batch_size)

        metadata = load_meta(self.data_file.encode("ascii"))
        self.class_names = [metadata.names[i].decode("ascii") for i in range(metadata.classes)]
        self.class_colors = class_colors(self.class_names)
        self.network_w = lib.network_width(self.network)
        self.network_h = lib.network_height(self.network)

        # return network, class_names, colors

    def detect_image(self, dk_image, resized_rgb):
        """
        Returns a list with highest confidence class and their bbox
        """
        # dk_image = make_image(self.network_w, self.network_h, 3)
        copy_image_from_bytes(dk_image,resized_rgb.tobytes())

        pnum = pointer(c_int(0))
        predict_image(self.network, dk_image)
        detections = get_network_boxes(self.network, dk_image.w, dk_image.h,
                        self.thresh, self.hier_thresh, None, 0, pnum, 0)
        num = pnum[0]
        if self.nms:
            do_nms_sort(detections, num, len(self.class_names), self.nms)
        predictions = remove_negatives( detections, self.class_names, num)
        predictions = decode_detection(predictions)
        free_detections(detections, num)
        free_image(dk_image)
        return sorted(predictions, key=lambda x: x[1])

count = 0
def YOLO(resized_rgb):
    """ needs resized rgb frame """
    global count

    darknet_image = make_image(network_width(netMain),network_height(netMain),3)
    """ image is already resized and rgb by sender (client) (w512, h416) """
    copy_image_from_bytes(darknet_image,resized_rgb.tobytes())

    detections = detect_image(netMain, metaMain, darknet_image, thresh=0.75)
    if detections:
        if detections[0][1] > 0.95:
            count += 1
            print('detected:',str(count))
            if count >= 10:
                return (detections)
            else: return (None)
        else: 
            count = count - 3 #rarely 
            return (None)
    else:
        count = 0
        return (None)

hasGPU=True

lib = CDLL("./libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

#copy image from bytes
copy_image_from_bytes = lib.copy_image_from_bytes
copy_image_from_bytes.argtypes = [IMAGE,c_char_p]

if hasGPU:
    set_gpu = lib.cuda_set_device
    set_gpu.argtypes = [c_int]

#init cpu
init_cpu = lib.init_cpu

#make image
make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

#load net custom
load_net_custom = lib.load_network_custom
load_net_custom.argtypes = [c_char_p, c_char_p, c_int, c_int]
load_net_custom.restype = c_void_p

#load meta
load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

#get network boxes
get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int), c_int]
get_network_boxes.restype = POINTER(DETECTION)

#free detections
free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

#goddamn_predictor
predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

#do_nms_sort
do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

