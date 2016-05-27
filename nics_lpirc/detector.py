# -*- coding: utf-8 -*-

from fast_rcnn.test import im_detect
from fast_rcnn.config import cfg as f_cfg
import caffe

class Detector(object):
    def __init__(self, cfg):
        self.proto = cfg.detector.proto
        self.model = cfg.detector.model
        self.net = caffe.Net(self.proto, self.model, caffe.TEST)
        if cfg.detector.cpu_mode:
            caffe.set_mode_cpu()
        else:
            caffe.set_mode_gpu()
            caffe.set_device(cfg.detector.device_id)
            f_cfg.GPU_ID = cfg.detector.device_id

    def detect(self, im):
        scores, boxes = im_detect(self.net, im)
        return scores, boxes
