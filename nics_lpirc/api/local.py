# -*- coding: utf-8 -*-

import os
import sys

import cv2

from nics_lpirc.api import APIAdapter

class LocalAPI(APIAdapter):
    def __init__(self, cfg):
        self.local_dir = cfg.localapi.local_dir
        self.single_res_file = cfg.localapi.single_res_file
        if self.single_res_file == "":
            self.res_dir = cfg.localapi.res_dir
            if not os.path.exists(self.res_dir):
                os.mkdir(self.res_dir)
        else:
            self._res_file = open(self.single_res_file, "w")

        self.file_list = os.listdir(self.local_dir)
        self.num_files = len(self.file_list)
        self.index = 0

    def get_image(self):
        fname = self.file_list[self.index]
        #print fname
        try:
            im = cv2.imread(os.path.join(self.local_dir, fname))
        except Exception as e:
            print >>sys.stderr, "Exception in reading image, ignore this image %s: " % fname, e
        im_id = "%d_%s" % (self.index, fname)
        self.index += 1
        return im_id, im

    def commit_result(self, im_id, class_ids, dets):
        if self.single_res_file != "":
            wf = self._res_file
        else:
            wf = open(os.path.join(self.res_dir, im_id), "w")
        for index in range(len(class_ids)):
            wf.write("%s %d %f %f %f %f %f\n" % (im_id, class_ids[index],
                                                 dets[index][4], dets[index][0],
                                                 dets[index][1], dets[index][2],
                                                 dets[index][3]))

    def done(self):
        return self.index >= self.num_files

    @classmethod
    def get_image_by_id(cls, cfg, im_id):
        ldir = cfg.localapi.local_dir
        _, fname = im_id.split("_", 1)
        try:
            return cv2.imread(os.path.join(ldir, fname))
        except Exception as e:
            print >>sys.stderr, "Exception in reading image, ignore this image %s: " % fname, e
            return None
