# -*- coding: utf-8 -*-

from multiprocessing import Process, Queue
import time

class NotImplementedError(Exception):
    pass

class APIAdapter(object):
    def get_image(self):
        raise NotImplementedError()

    def commit_result(self, im_id, class_ids, dets):
        self._commit_result(im_id, class_ids, dets)

    def _commit_result(self, im_id, class_ids, dets):
        raise NotImplementedError()

    def done(self):
        raise NotImplementedError()

    def commiter_start(self):
        pass

    def commiter_done(self):
        pass

    def commiter_kill(self):
        pass

    def commiter_join(self):
        pass

    @classmethod
    def get_image_by_id(cls, cfg, im_id):
        raise NotImplementedError()

    def __iter__(self):
        while not self.done():
            im_id, im = self.get_image()
            if im is not None:
                yield((im_id, im))
        yield((None, None))

class SubprocessAPIAdapter(APIAdapter):
    def __init__(self, cfg):
        self.queue_size = cfg.runner.queue_size # use the same queue size as fetch process?
        self._started = False

    def commiter_start(self):
        self.commit_queue = Queue(self.queue_size)
        self.commit_process = Process(target=self.commiter, args=(self,))
        self.commit_process.start()
        self._started = True

    @staticmethod
    def commiter(self):
        print "Commiter process start!"
        while 1:
            obj = self.commit_queue.get()
            if obj is not None:
                image_id, class_ids, dets = obj
                self._commit_result(image_id, class_ids, dets)
            else:
                print "All results commited!"
                break

    def commit_result(self, im_id, class_ids, dets):
        self.commit_queue.put((im_id, class_ids, dets))

    def commiter_done(self):
        self.commit_queue.put(None)

    def commiter_kill(self):
        if self._started:
            print "Terminating the commiter process"
            self.commit_process.terminate()
            self.commit_process.join()
        else:
            print "Terminating the commiter process: not running"
            
    def commiter_join(self):
        self.commit_process.join()
