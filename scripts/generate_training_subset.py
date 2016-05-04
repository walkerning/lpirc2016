# -*- coding: utf-8 -*-
"""
按照类别/抽取用于训练的数据
"""
import argparse
import os
import sys
import random

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--subset", required=True, help="Python expression to eval to get the list of the classes you want")
parser.add_argument("-o", "--output", required=True, help="Output file.")
parser.add_argument("-q", "--quiet", action="store_true", help="Do not print out details")
group = parser.add_mutually_exclusive_group()
group.add_argument("-n", "--num", type=int, help="The number of postive samples of each class")
group.add_argument("-p", "--percentage", type=float, help="The percentage of each class")

args = parser.parse_args()

devkit_path = os.environ.get("ILSVRC_DEVKIT_DIR", None)
imagenet_data_path = os.environ.get("IMAGENET_DATA_DIR", None)

# 检查环境变量
if devkit_path is None:
    print >>sys.stderr, u"需要设置环境变量ILSVRC_DEVKIT_DIR"
    sys.exit(1)
if imagenet_data_path is None:
    print >>sys.stderr, u"需要设置环境变量IMAGENET_DATA_DIR"
    sys.exit(1)

train_dir = os.path.join(devkit_path, *("data", "det_lists"))
data_dir = os.path.abspath(os.path.join(imagenet_data_path, "ILSVRC2014_DET_train"))

# 现在只拿positive samples
cls_list = eval(args.subset)
img_set = set()
ps_num = 0
for index in set(cls_list):
    t_file = os.path.join(train_dir, "train_pos_%d.txt" % index)
    with open(t_file, "r") as f:
        #names = f.read().strip().split("\n")#[name for name in f.readlines() if name.startswith("ILSVRC2014_train_")]
        names = f.readlines()
        random.shuffle(names)
        img_num = len(names)
        if args.num is not None:
            if args.num > img_num:
                print u"类别 %d 只有 %d 张训练图片, 不到 %d, 全部选取" % (index, img_num, args.num)
            else:
                names = names[:args.num]
        if args.percentage is not None:
            num = int(img_num * args.percentage)
            names = names[:num]
        if not args.quiet:
            print u"类别 %d 保留 %d positive samples" % (index, len(names))
        ps_num += len(names)
        img_set.update(set(names))

# 随机shuffle训练数据
# set is not guaranted to be ordered or random, let us shuffle it again
img_list = list(img_set)
random.shuffle(img_list)
img_list = [os.path.join(data_dir, img) for img in img_list]
img_num = len(img_list)
with open(args.output, "w") as f:
    for name in img_list:
        f.write(name)
if not args.quiet:
    print u"总sample num: %d, 总image num: %d" % (ps_num, img_num)
