# -*- coding: utf-8 -*-

import argparse
import sys
import cPickle
import re

import matplotlib.pyplot as plt

from nics_lpirc.config import Config
from nics_lpirc.util import import_class

class Visualizer(object):
    def __init__(self, res_file, api_cls, cfg, thresh=0.5, cls_dict=None):
        self.res_file = res_file
        self.api_cls = api_cls
        self.cfg = cfg

        # only plot the boxes with score beyond thresh
        self.vis_thresh = thresh

        # cls_index to cls_name mapping
        self.cls_dict = cls_dict or {}

        self.im_dict = {}

    def visualize(self):
        with open(self.res_file, "r") as f:
            lines = f.read().strip().split("\n")
            for ind in range(len(lines)):
                l = lines[ind]
                im_id, cls_ind, score, bbox_str = re.split("[ \t]+", l, 3)
                score = float(score)
                if score <= self.vis_thresh:
                    continue
                # gather bbox detection information by image id
                self.im_dict.setdefault(im_id, []).append({
                    "cls_ind": cls_ind,
                    "cls_name": self.cls_dict.get(int(cls_ind), cls_ind),
                    "score": score,
                    "bbox": [float(x) for x in bbox_str.split(" ")]
                })
        vis_ind = 0

        for im_id, det_infos in self.im_dict.iteritems():
            # get image using the API classmethod get_image_by_id
            im = self.api_cls.get_image_by_id(self.cfg, im_id)
            if im is None:
                continue

            fig, ax = plt.subplots(figsize=(12, 12))
            # draw the original image
            im = im[:, :, (2, 1, 0)]
            ax.imshow(im, aspect="equal")

            for det_info in det_infos:
                bbox = det_info["bbox"]
                ax.add_patch(
                    plt.Rectangle((bbox[0], bbox[1]),
                                  bbox[2] - bbox[0],
                                  bbox[3] - bbox[1], fill=False,
                                  edgecolor='red', linewidth=3.5)
                )
                ax.text(bbox[0], bbox[1] - 2,
                        '{cls_name} {score}'.format(**det_info),
                        bbox=dict(facecolor='blue', alpha=0.5),
                        fontsize=14, color='white')

            ax.set_title(('{} detections with '
                          'p( is_obj | box ) >= {:1f}'.format(im_id, self.vis_thresh)),
                         fontsize=14)
            print "%d: image %s handled, %d boxes ploted" % (vis_ind, im_id, len(det_infos))
            vis_ind += 1
            plt.axis("off")
            plt.tight_layout
            plt.draw()

        # show all the plots
        plt.show()

def visualize():
    parser = argparse.ArgumentParser(
        prog="lpirc_vis",
    )
    parser.add_argument("-f", "--file", required=True, dest="res_file", metavar="RES_FILE", help="Load results from RES_FILE")
    parser.add_argument("-c", "--config", required=True, metavar="CONF", help="Load configurations from FILE")
    parser.add_argument("-d", "--dict", metavar="DICT", dest="cls_dict", help="Load the index-to-name dict of classes from DICT(in pickle format)")
    parser.add_argument("--api", metavar="API_CLS", help="Use API_CLS for getting images and commit result", default="api.HttpAPI")
    parser.add_argument("-t", "--thresh", type=float, metavar="THRESH", help="Score threshold of bboxes for visualization", default=0.5)
    args = parser.parse_args()

    if not args.api.startswith("nics_lpirc.api."):
        args.api = "nics_lpirc.api." + args.api
    api_cls = import_class(args.api)

    cfg = Config.from_file(args.config)
    if not hasattr(args, "cls_dict") or not args.cls_dict:
        print >>sys.stderr, "Warning: No ind-to-name dict is given!"
        cls_dict = {}
    else:
        with open(args.cls_dict, "r") as f:
            cls_dict = cPickle.load(f)

    vis = Visualizer(args.res_file, api_cls, cfg, thresh=args.thresh, cls_dict=cls_dict)
    vis.visualize()

if __name__ == "__main__":
    visualize()
