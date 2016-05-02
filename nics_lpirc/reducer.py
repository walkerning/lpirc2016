# -*- coding: utf-8 -*-

import numpy as np
from fast_rcnn.nms_wrapper import nms

class BoxReducer(object):
    def __init__(self, cfg):
        self.max_per_image = cfg.reducer.max_per_image
        self.thresh = cfg.reducer.score_thresh
        self.num_classes = cfg.general.num_classes
        self.IoU_thresh = cfg.reducer.IoU_thresh
        self.force_cpu = cfg.reducer.cpu_nms

    def reduce_boxes(self, scores, boxes):
        """
        Reduce the result boxes
        """
        box_classes = []
        all_dets = np.array([], dtype="float32")
        box_scores = np.array([], dtype="float32")
        for j in xrange(1, self.num_classes):
            # single-class NMS
            inds = np.where(scores[:, j] > self.score_thresh)[0]
            cls_scores = scores[inds, j]
            cls_boxes = boxes[inds, j*4:(j+1)*4]
            cls_dets = np.hstack((cls_boxes, cls_scores[:, np.newaxis])) \
                         .astype(np.float32, copy=False)
            keep = nms(cls_dets, self.IoU_thresh, self.force_cpu)
            # use vstack or list
            box_classes += [j] * len(keep)
            cls_dets = cls_dets[keep, :]
            box_scores = np.append(box_scores, cls_scores[keep])
            all_dets = np.vstack(all_dets, cls_dets)

        # Limit to max_per_image detections *over all classes*
        if len(box_classes) > self.max_per_image:
            indexes = np.argsort(-box_scores)[:self.max_per_image]
            all_dets = all_dets[indexes, :]
        box_classes = np.array(box_classes, dtype=int)[indexes]

        return (box_classes, all_dets)
