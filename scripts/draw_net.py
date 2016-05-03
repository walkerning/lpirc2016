# -*- coding: utf-8 -*-
"""
Simple wrapper script around caffe.draw_net_to_file

eg. python draw_net.py Res-50.prototxt Res-50.png
"""

from google.protobuf import text_format

from caffe import draw
from caffe.proto import caffe_pb2

def draw_from_proto(fname, wname):
    net_param = caffe_pb2.NetParameter()
    text_format.Merge(open(fname, "r").read(), net_param)
    draw.draw_net_to_file(net_param, wname)

if __name__ == "__main__":
    import sys
    draw_from_proto(sys.argv[1], sys.argv[2])
