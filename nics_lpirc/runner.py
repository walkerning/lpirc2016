# -*- coding: utf-8 -*-

import argparse
from multiprocessing import Process, Queue
import time
import sys
import traceback

from fast_rcnn.config import cfg as f_cfg

from nics_lpirc.api import APIAdapter
from nics_lpirc.reducer import BoxReducer
from nics_lpirc.detector import Detector
from nics_lpirc.util import import_class
from nics_lpirc.config import Config

fetch_process = None

class Runner(object):
    def __init__(self, api_cls, detector_cls, reducer_cls, cfg):
        # patch fast_rcnn.config.cfg
        f_cfg.TEST.HAS_RPN = True
        if not issubclass(api_cls, APIAdapter):
            raise ValueError("`api_cls` should be an subclass of class `APIAdapter`")
        self.api_ada = api_cls(cfg)
        if not issubclass(detector_cls, Detector):
            raise ValueError("`detector_cls` should be an subclass of class `Detector`")
        self.detector = detector_cls(cfg)
        if not issubclass(reducer_cls, BoxReducer):
            raise ValueError("`reducer_cls` should be an subclass of class `BoxReducer`")
        self.reducer = reducer_cls(cfg)

        # initialize queue
        self.queue_size = cfg.runner.queue_size
        self.queue = Queue(self.queue_size)

    @staticmethod
    def fetch_image(api_ada, queue):
        for im in api_ada:
            queue.put(im)

    def detect(self, im):
        scores, boxes = self.detector.detect(im)
        class_ids, dets = self.reducer.reduce_boxes(scores, boxes)
        return class_ids, dets

    def run(self):
        global fetch_process
        fetch_process = Process(target=Runner.fetch_image, args=(self.api_ada, self.queue))
        fetch_process.start()
        # Q: 是否应该在此进程读图像文件, 而不是从queue里拿image
        im_id, im = self.queue.get()
        while im_id is not None:
            class_ids, dets = self.detect(im)
            self.api_ada.commit_result(im_id, class_ids, dets)
            im_id, im = self.queue.get()

        fetch_process.join()

def terminate_fetch_process():
    if fetch_process is not None and fetch_process.is_alive():
        print "Terminating the subprocess..."
        fetch_process.terminate()
        time.sleep(0.1)
        if fetch_process.is_alive():
            print "Error: Subprocess is still alive!!!"
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        prog="lpirc_detect",
    )
    parser.add_argument("-c", "--config", required=True, metavar="FILE", help="Load configurations from FILE")
    parser.add_argument("--api", metavar="API_CLS", help="Use API_CLS for getting images and commit result", default="api.HttpAPI")
    args = parser.parse_args()

    if not args.api.startswith("nics_lpirc."):
        args.api = "nics_lpirc." + args.api

    cfg = Config.from_file(args.config)
    runner = Runner(import_class(args.api), Detector, BoxReducer, cfg)
    try:
        runner.run()
    except Exception as e:
        print "%s: %s" % (e.__class__.__name__, e)
        traceback.print_exc()
        terminate_fetch_process()
    except:
        # try to terminate the subprocess when something unexpected happened.
        terminate_fetch_process()

if __name__ == "__main__":
    main()
