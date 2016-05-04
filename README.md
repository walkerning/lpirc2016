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

**本地跑ILSVRC的validate数据集**

1. 设置好 `${IMAGENET_DATA_DIR}` 环境变量, 在eva2上是 `/home/imgNet/DATA/`
2. 设置好 `${ILSVRC_DEVKIT_DIR}` 环境变量, 从ILSVRC官网下载devkit
3. `cp lpirc.conf.sample myconfig.conf`, 然后根据自己的需求修改配置文件 (默认配置文件应该直接就能跑)
3. 运行:
   ```bash
   lpirc_detect  -c <config file> --api val.ValAPI
   ```
4. 如果没有修改配置文件中的 `valapi -> res_file` 配置，生成的结果存在当前目录下的 `val_res.txt` 里

### Test and Debug

**Visualizing**

记得使用 `ssh -Y <server>` 登陆打开SSH的X-Forwarding和xauth信任.

```bash
lpirc_vis -f --api local.LocalAPI -d scripts/cls_dict.pkl <path/to/your/result_file> -c <path/to/your/conf>
```

**Profiling**

使用`lpirc_detect_prof`带profiling的运行程序, 暂时所有profiling结果输出在标准输出

```bash
lpirc_detect_prof -c ./lpirc.conf --api local.LocalAPI
```

示例效果:

```
1        detector.detect(im_detect)     start...
1        detector.detect(im_detect)     finish..  elapsed 0.852118 average 0.852118
1        reducer.reduce_boxes           start...
1        reducer.reduce_boxes           finish..  elapsed 0.011326 average 0.011326
1        localapi.commit_result         start...
1        localapi.commit_result         finish..  elapsed 0.000080 average 0.000080
2        detector.detect(im_detect)     start...
2        detector.detect(im_detect)     finish..  elapsed 0.231513 average 0.541816
2        reducer.reduce_boxes           start...
2        reducer.reduce_boxes           finish..  elapsed 0.011364 average 0.011345
2        localapi.commit_result         start...
2        localapi.commit_result         finish..  elapsed 0.000048 average 0.000064
3        detector.detect(im_detect)     start...
3        detector.detect(im_detect)     finish..  elapsed 0.229383 average 0.437671
3        reducer.reduce_boxes           start...
3        reducer.reduce_boxes           finish..  elapsed 0.010686 average 0.011125
3        localapi.commit_result         start...
3        localapi.commit_result         finish..  elapsed 0.000047 average 0.000058
4        detector.detect(im_detect)     start...
4        detector.detect(im_detect)     finish..  elapsed 0.229479 average 0.385623
4        reducer.reduce_boxes           start...
4        reducer.reduce_boxes           finish..  elapsed 0.010501 average 0.010969
4        localapi.commit_result         start...
4        localapi.commit_result         finish..  elapsed 0.000047 average 0.000055
5        detector.detect(im_detect)     start...
5        detector.detect(im_detect)     finish..  elapsed 0.239532 average 0.356405
5        reducer.reduce_boxes           start...
5        reducer.reduce_boxes           finish..  elapsed 0.011377 average 0.011051
5        localapi.commit_result         start...
5        localapi.commit_result         finish..  elapsed 0.000049 average 0.000054
Summary
----------------------------------------
name                           average  total    called
detector.detect(im_detect)     0.356405 1.782025        5
reducer.reduce_boxes           0.011051 0.055254        5
localapi.commit_result         0.000054 0.000271        5
httpapi.commit_result          0.000000 0.000000        0
```

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

- [x] HTTP api实现
- [x] 可视化脚本
- [x] profiling, 方便之后做各种参数的选择
- [x] evaluation脚本: 实现了一个 `ValAPI` 用于在val集上生成结果. 使用ILSVRC devkit自己的matlab脚本测试
- [ ] 在caffe/py-faster-rcnn代码中进行减少测试内存的修改
- [ ] 等训练的进一步进展, 联调调参数