# -*- coding: utf-8 -*-

def import_class(classname):
    mod_name, cls_name = classname.rsplit(".", 1)
    try:
        module = __import__(mod_name, fromlist=["*"])
    except ImportError:
        raise
    cls = getattr(module, cls_name)
    return cls
