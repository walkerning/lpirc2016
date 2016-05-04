# -*- coding: utf-8 -*-
"""
按照类别/抽取用于训练的数据
"""

import os
import sys
import argparse
import random
import itertools

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--subset", required=True, help="Python expression to eval to get the list of the classes you want")
parser.add_argument("-a", "--additional", action="append", help="Add additional data list file")
parser.add_argument("-b", "--additional-base", action="append", help="Add additional data base directory")
parser.add_argument("-o", "--output", required=True, help="Output file.")
parser.add_argument("-q", "--quiet", action="store_true", help="Do not print out details")
parser.add_argument("-v", "--val", metavar="VAL_FILE", help="Use those which are not choosed as training data as validation images, put them into VAL_FILE")

group = parser.add_mutually_exclusive_group()
group.add_argument("-n", "--num", type=int, help="The number of positive samples that will be used as training"
                   " data for each class")
group.add_argument("-p", "--percentage", type=float, help="The percentage of positive samples that will be used"
                   " as training data for each class")

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

cls_list = eval(args.subset)
cls_tnames = [os.path.join(train_dir, "train_pos_%d.txt" % index) for index in cls_list]
file_items = zip(cls_tnames, [data_dir] * len(cls_list))

# 处理额外的list文件
if args.additional:
    num_additional = len(args.additional)
    num_base = len(args.additional_base)
    if num_base == 1:
        args.additional_base = args.additional_base * num_additional
    elif num_base == 0:
        args.additional_base = [data_dir] * num_additional
    elif num_base != num_additional:
        print >>sys.stderr, ("Number of argument `-b, --additional-base` %d incorrect," 
                             "must be 0 or 1 or the same as the number"
                             " of additional files %d") % (num_base, num_additional)
        sys.exit(1)
    add_file_items = zip(args.additional, args.additional_base)
else:
    add_file_items = []

# 现在只拿positive samples
img_set = set()
if args.val:
    val_set = set()
ps_num = 0

# handle set from the ILSVRC-devkit standard postive training data list
for index, (t_file, path) in enumerate(itertools.chain(file_items, add_file_items)):
    with open(t_file, "r") as f:
        # ignore training data of ILSVRC2013
        names = [os.path.join(path, name.strip().split(" ")[0]) for name in f.readlines() if name.startswith("ILSVRC20")]
        #names = f.readlines()
    random.shuffle(names)

    img_num = len(names)
    if args.num is not None:
        if args.num > img_num:
            print u"类别 %d 只有 %d 张训练图片, 不到 %d, 全部选取为训练图片" % (index, img_num, args.num)
        else:
            if args.val:
                val_set.update(set(names[args.num:]))
            names = names[:args.num]

    if args.percentage is not None:
        num = int(img_num * args.percentage)
        if args.val:
            val_set.update(set(names[num:]))
        names = names[:num]
    if not args.quiet:
        print u"类别 %d 保留 %d positive samples 数据" % (index, len(names)),
        if args.val:
            print u", %d 作为validation数据" % (img_num - len(names))
        else:
            print
    ps_num += len(names)
    img_set.update(set(names))
    

# 随机shuffle训练数据
# set is not guaranted to be ordered or random, let us shuffle it again
img_list = list(img_set)
random.shuffle(img_list)
img_num = len(img_list)
with open(args.output, "w") as f:
    for name in img_list:
        f.write(name+"\n")

# validation list
if args.val:
    # 不使用训练数据做validate是基本素养!
    val_set = val_set - img_set
    val_list = list(val_set)
    random.shuffle(val_list)
    if not args.quiet:
        print "总sample validation image数: %d" % len(val_list)
    with open(args.val, "w") as f:
        for name in val_list:
            f.write(name+"\n")

# print some information
if not args.quiet:
    print u"总sample num: %d, 总image num: %d" % (ps_num, img_num)
