# -*- coding: utf-8 -*-

import os
import sys

import cv2

from nics_lpirc.api import APIAdapter

class ValAPI(APIAdapter):
    def __init__(self, cfg):
        self.local_dir = cfg.valapi.pic_dir
        self.val_file = cfg.valapi.val_file

        # open result file
        self.res_file = cfg.valapi.res_file
        self._res_file = open(self.res_file, "w")

        with open(self.val_file, "r") as f:
            lines = f.read().strip().split("\n")
        self.file_list = [l.split(" ", 1)[0] for l in lines]
        self.num_files = len(self.file_list)
        self.index = 0

    def get_image(self):
        fname = self.file_list[self.index] + ".JPEG"
        abs_fname = os.path.join(self.local_dir, fname)
        #print abs_fname

        # index in val.txt is 1-based
        im_id = "%d" % (self.index + 1)
        try:
            im = cv2.imread(abs_fname)
        except Exception as e:
            print >>sys.stderr, "im_id: %d: Ignore this image! Exception in reading image: %s: " % (im_id, abs_fname), e
        if im is None:
            print >>sys.stderr, "im_id %s: Ignore this image! Readed image is `None`, please confirm the image exists." % im_id

        self.index += 1
        return im_id, im

    def commit_result(self, im_id, class_ids, dets):
        for index in range(len(class_ids)):
            self._res_file.write("%s %d %f %f %f %f %f\n" % (im_id, class_ids[index],
                                                             dets[index][4], dets[index][0],
                                                             dets[index][1], dets[index][2],
                                                             dets[index][3]))

    def done(self):
        return self.index >= self.num_files

    @classmethod
    def get_image_by_id(cls, cfg, im_id):
        index = int(im_id)
        val_file = cfg.valapi.val_file
        ldir = cfg.valapi.pic_dir
        with open(val_file, "r") as f:
            for line in f:
                index -= 1
                if index <= 0:
                    fname = line.split(" ", 1)[0] + ".JPEG"
                    break
        try:
            abs_fname = os.path.join(ldir, fname)
            im = cv2.imread(abs_fname)
            if im is None:
                print >>sys.stderr, "Failed to read a valid image, ignore this image %s: " % abs_fname, e
        except Exception as e:
            print >>sys.stderr, "Exception in reading image, ignore this image %s: " % abs_fname, e
            return None
        return im
