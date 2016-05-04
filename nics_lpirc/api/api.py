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

    @classmethod
    def get_image_by_id(cls, cfg, im_id):
        raise NotImplementedError()

    def __iter__(self):
        while not self.done():
            im_id, im = self.get_image()
            if im is not None:
                yield((im_id, im))
        yield((None, None))
