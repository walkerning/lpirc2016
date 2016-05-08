# -*- coding: utf-8 -*-
"""
Simple wrapper script around caffe.draw_net_to_file

eg. python draw_net.py Res-50.prototxt Res-50.png
"""
import sh
import os

from google.protobuf import text_format

from caffe import draw
from caffe.proto import caffe_pb2

def draw_from_proto(fname, wname):
    if os.path.isdir(fname):
        sh.mkdir("-p", wname)
        for base in os.listdir(fname):
            sub_fname = os.path.join(fname, base)
            if os.path.isdir(sub_fname):
                sub_wname = base
            else:
                sub_wname = base + ".png"
            draw_from_proto(sub_fname, os.path.join(wname, sub_wname))
    else:
        if not (fname.endswith(".pt") or fname.endswith(".prototxt")):
            print "Ignore file %s according to its suffix, not `pt` or `prototxt`" % fname
            return
        if "solver" in fname:
            print "Regard file %s as a solver prototxt, ignore!" % fname
            return
        net_param = caffe_pb2.NetParameter()
        text_format.Merge(open(fname, "r").read(), net_param)
        draw.draw_net_to_file(net_param, wname)

if __name__ == "__main__":
    import sys
    draw_from_proto(sys.argv[1], sys.argv[2])
