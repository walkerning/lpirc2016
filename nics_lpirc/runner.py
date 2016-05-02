# -*- coding: utf-8 -*-

import argparse
from multiprocessing import Process, Queue

from nics_lpirc.api import APIAdapter
from nics_lpirc.reducer import BoxReducer
from nics_lpirc.detector import Detector
from nics_lpirc.util import import_class
from nics_lpirc.config import Config

class Runner(object):
    def __init__(self, api_cls, detector_cls, reducer_cls, cfg):
        # Is there any need to patch fast_rcnn.config?
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
        score, boxes = self.detector.detect(im)
        class_ids, dets = self.reducer.reduce_boxes()
        return class_ids, dets

    def run(self):
        fetch_process = Process(target=Runner.fetch_image, args=(self.api_ada, self.queue))
        fetch_process.start()
        im = self.queue.get()
        while im is not None:
            class_ids, dets = self.detect(im)
            self.api_ada.commit_result(self, class_ids, dets)
            im = self.queue.get()

        fetch_process.join()

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
    runner.run()

if __name__ == "__main__":
    main()
