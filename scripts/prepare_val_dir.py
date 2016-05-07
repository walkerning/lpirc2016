# -*- coding: utf-8 -*-
"""
简单的准备val目录的脚本(见README中拆分数据一节)
"""

import os
import sys
import sh

if len(sys.argv) != 4:
    print >>sys.stderr, u"用法: python prepare_val_dir.py val_no_index.txt img_dir gt_dir"
    sys.exit(1)

val_file = sys.argv[1]
img_dir = sys.argv[2]
gt_dir = sys.argv[3]

if os.path.exists(gt_dir):
    print >>sys.stderr, u"目录 %s 存在, 请先删除之" % gt_dir
    sys.exit(1)

if os.path.exists(img_dir):
    print >>sys.stderr, u"目录 %s 存在, 请先删除之" % img_dir
    sys.exit(1)

try:
    sh.mkdir("-p", img_dir)
    sh.mkdir("-p", gt_dir)
except Exception as e:
    print >>sys.stderr, u"创建目录失败: %s" % e

number = 0
with open(val_file, "r") as f:
    for abs_fname in f:
        abs_fname = abs_fname.strip() 
        if not abs_fname:
            continue
        # this just follow the local name convetion
        if not abs_fname.endswith(".JPEG"):
            abs_img_fname = abs_fname + ".JPEG"
            abs_gt_fname = abs_fname.replace("DET_", "DET_bbox_", 1) + ".xml"
        else:
            abs_img_fname = abs_fname
            abs_gt_fname = abs_fname.replace("DET_", "DET_bbox_", 1).replace(".JPEG", ".xml")

        sh.ln("-s", abs_img_fname, os.path.join(img_dir,
                                                os.path.basename(abs_img_fname)))
        sh.ln("-s", abs_gt_fname, os.path.join(gt_dir,
                                               os.path.basename(abs_gt_fname)))
        number += 1

print u"一共 %d 个图片和标注被软链接到 %s 和 %s 目录下, " % (number, img_dir, gt_dir)
