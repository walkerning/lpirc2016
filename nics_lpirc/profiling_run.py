# -*- coding: utf-8 -*-

import sys
import os
import time
import datetime
import atexit
from functools import wraps
from multiprocessing import Process
import sh

from utils.timer import Timer # in fast_rcnn

from nics_lpirc.reducer import BoxReducer
from nics_lpirc.detector import Detector
from nics_lpirc.runner import Runner
from nics_lpirc.runner import main as _main
from nics_lpirc.api.local import LocalAPI
from nics_lpirc.api.http import HttpAPI
from nics_lpirc.api.val import ValAPI

global_timer_dict = {}

def summary(sort_key="average_time", file=sys.stdout):
    """
    Parameters
    ----------------
    sort_key: str
        Should be one of "average_time" or "total_time"
    """
    print >>file, "Summary\n" + "-" * 40
    print >>file, "{:30s} {:8s} {:8s} {:8s}".format("name", "average", "total", "called")
    sorted_items = sorted(global_timer_dict.items(), key=lambda item: getattr(item[1][0], sort_key, 0), reverse=True)
    for item in sorted_items:
        print >>file, "{:30s} {:8f} {:8f} {:8d}".format(item[0], item[1][0].average_time, item[1][0].total_time, len(item[1][1]))

def patch_all():
    BoxReducer.reduce_boxes = profile_func(BoxReducer.reduce_boxes, "reducer.reduce_boxes")
    Detector.detect = profile_func(Detector.detect, "detector.detect(im_detect)")
    #ValAPI.commit_result = profile_func(ValAPI.commit_result, "valapi.commit_result")
    #Runner.detect = profile_func(Runner.detect, "runner.detect")
    #LocalAPI.commit_result = profile_func(LocalAPI.commit_result, "localapi.commit_result")
    HttpAPI.commit_result = profile_func(HttpAPI.commit_result, "httpapi.commit_result")
    HttpAPI._commit_result = profile_func(HttpAPI._commit_result, "httpapi.real_commit_result") # FIXME: 由于使用了多进程这个结果暂时不会被Summary记录
    atexit.register(summary)

def profile_func(func, name):
    profile_list = []
    timer = Timer()
    global_timer_dict[name] = (timer, profile_list)
    @wraps(func)
    def _func(*args, **kwargs):
        # Warn: we do not check for arguments here!
        called = len(profile_list) + 1
        print "{:<8d} {:30s} start...  ".format(called, name)
        timer.tic()
        
        # actually call the function
        ans = func(*args, **kwargs)

        single_time = timer.toc(average=False)
        print "{:<8d} {:30s} finish..  elapsed {:8f} average {:8f}".format(called, name, single_time, timer.average_time)
        profile_list.append(single_time)

        return ans
    return _func

# monkey patch all computations that we concern
patch_all()

def evaluate_mem(_pid, logfile):
    """
    Use the ps command for profiling memory for now.
    """
    print "Start benchmarking the RSS memory usage, result will be in " + logfile
    with open(logfile, "w") as wf:
        while 1:
            info = sh.awk(sh.tr(sh.ps("aux"), "-s", "' '"), "-vpid={}".format(_pid), "{if ($2==pid) {print $6}}").strip()
            wf.write("{:<12s}: {:10s}\n".format(str(datetime.datetime.now()), info))
            wf.flush() # FIXME: ugly solution here
            time.sleep(1)
    
def main():
    self_pid = os.getpid()
    memory_eval_process = Process(target=evaluate_mem, args=(self_pid, "memory_use.log"))
    memory_eval_process.start()
    _main()
    memory_eval_process.terminate()
    memory_eval_process.join()
