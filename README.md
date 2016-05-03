LPIRC 2016
================

使用
----------------

### Install
```bash
python setup.py develop
```


为了方便用不同的faster RCNN build测试，现在先不使用`git submodule`并自动设置`sys.path`的形式.
所以需要自己设置好 `PYTHONPATH` 环境变量

```bash
export PYTHONPATH="/path/to/pycaffe:/path/to/py-faster-rcnn/lib:${PYTHONPATH}"
```

### Config

`lpirc.conf.sample`里是一个示例配置文件

```bash
cp lpirc.conf.sample lpirc.conf # 复制并编辑lpirc.conf, 修改配置
```

### Run

```bash
lpirc_detect  -c <config file> --api <fully-qualified import path of api class or the import path relative to nics_lpirc>
# eg. lpirc_detect -c ./lpirc.conf --api local.LocalAPI
```

### Test and Debug

**Visualizing**

记得使用 `ssh -Y <server>` 登陆打开SSH的X-Forwarding和xauth信任.

```bash
lpirc_vis -f --api local.LocalAPI -d scripts/cls_dict.pkl <path/to/your/result_file> -c <path/to/your/conf>
```

**Profiling**

### Problems

如果是调用caffe的c++过程们中间出错退出, 不能在Python的`atexit`和`except:`里面抓到, 导致子进程不能被安全的退出。应该要开两个进程，另一个进程负责管理. 不过感觉对于正确情况没必要, 所以不实现了


开发
----------------

### Arch

使用Faster-RCNN, 只需要两个进程, image-fetching进程和Faster-RCNN detect进程.

```
+----------------+  image  +-------------------------+
|image-fetching  |-------->|   Faster-RCNN detector  |
+---------------^+         +-+-----------------------+
                |image       | answers
                |            |
              +-+------------v+
              |   HTTP server |
              +---------------+
```

### TODO

- [ ] HTTP api实现
- [ ] 可视化脚本
- [ ] profiling, 方便之后做各种参数的选择

