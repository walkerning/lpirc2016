# -*- coding: utf-8 -*-

class NotImplementedError(Exception):
    pass

class APIAdapter(object):
    def get_image(self):
        raise NotImplementedError()

    def commit_result(self, class_ids, dets):
        raise NotImplementedError()

    def done(self):
        raise NotImplementedError()

    def __iter__(self):
        while not self.done():
            im_id, im = self.get_image()
            yield((im_id, im))
        yield((None, None))

class HttpAPI(APIAdapter):
    def __init__(self, cfg):
        pass

    def get_image(self):
        pass

    def commit_result(self, class_ids, dets):
        pass

    def done(self):
        pass