# -*- coding: utf-8 -*_

from fast_rcnn.test import im_detect
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

    def detect(self, im):
        scores, boxes = im_detect(self.net, im)
        print scores, boxes
        return scores, boxes
