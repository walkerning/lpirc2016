# -*- coding: utf-8 -*-

from functools import wraps

from utils.timer import Timer # in fast_rcnn

from nics_lpirc.reducer import BoxReducer
from nics_lpirc.detector import Detector
from nics_lpirc.runner import (Runner, main)
from nics_lpirc.local import LocalAPI
from nics_lpirc.api import HttpAPI

def patch_all():
    #BoxReducer.reduce_boxes = profile_func(BoxReducer.reduce_boxes, "reducer.reduce_boxes")
    #Detector.detect = profile_func(Detector.detect, "detector.detect(im_detect)")
    Runner.detect = profile_func(Runner.detect, "runner.detect")
    LocalAPI.commit_result = profile_func(LocalAPI.commit_result, "localapi.commit_result")
    HttpAPI.commit_result = profile_func(HttpAPI.commit_result, "httpapi.commit_result")

def profile_func(func, name):
    profile_list = []
    timer = Timer()
    @wraps(func)
    def _func(*args, **kwargs):
        # Warn: we do not check for arguments here!
        called = len(profile_list) + 1
        print "{:<8d} {:20s} start...  ".format(called, name)
        timer.tic()
        
        # actually call the function
        ans = func(*args, **kwargs)

        single_time = timer.toc(average=False)
        print "{:<8d} {:20s} finish..  elapsed {:8f} average {:8f}".format(called, name, single_time, timer.average_time)
        profile_list.append(single_time)

        return ans
    return _func

# monkey patch all computations that we concern
patch_all()
