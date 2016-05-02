import toml

DEFAULT_CONF_STR = """
[general]
## In our case, we use 200-class imagenet dataset
num_classes = 201

[runner]
## The image queue size
queue_size = 8

[detector]
## Set cpu_mode to `true` to use cpu only
cpu_mode = false

## GPU device id to use
device_id = 0

## prototxt file
proto = "./fast_rcnn_test.pt"

## caffemodel file
caffemodel = "./fast_rcnn_test.caffemodel"

[reducer]
## Reduce to `max_per_image` boxes in one image
max_per_image = 5

## Boxes that has score beyond this threshold will be handled in NMS
score_thresh = 0.05

## Set `cpu_nms` to true to execute NMS on CPU
cpu_nms = false

[api]
"""

class Config(object):
    def __init__(self, cfg_dict):
        self.cfg_dict = toml.loads(DEFAULT_CONF_STR)
        for key, nested_dict in cfg_dict.iter_items():
            self.cfg_dict.set_defaults(key, dict()).update(nested_dict)

    def __getattr__(self, name):
        if name in self.cfg_dict:
            return self.cfg_dict[name]
        else:
            return super(Config, self).__getattr__(self, name)

    @classmethod
    def from_file(cls, file_name):
        return cls(toml.load(f))

    @classmethod
    def from_str(cls, cfg_str):
        return cls(toml.loads(cfg_str))


if __name__ == "__main__":
    cfg_str = """
[detector]
cpu_mode = false
proto = "./faster_rcnn_test.pt"
model = "./faster_rcnn_test.caffemodel"
"""
    cfg = Config.from_str(cfg_str)
    assert cfg.detector.cpu_mode == False
    assert cfg.detector.proto == "./faster_rcnn_test.pt"
    assert cfg.detector.model == "./faster_rcnn_test.caffemodel"

    cfg = Config.from_str(DEFAULT_CONF_STR)
    assert cfg.runner.queue_size == 8
    assert cfg.detector.device_id == 0
    assert cfg.general.num_classes == 201
    assert cfg.reducer.cpu_nms == False
    assert cfg.reducer.score_thresh == 0.05
