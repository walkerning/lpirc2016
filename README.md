LPIRC 2016
================

使用
----------------

### Install

**重要重要** 注意`--user`是**强制**的了!!! 不要用sudo装在系统路径, 因为大家在用一个container! 或者直接运行`make`. 

```bash
python setup.py develop --user
```

此时就应该可以在命令行中使用 `lpirc_detect`, `lpirc_detect_prof`, `lpirc_vis` 这三个命令. 
> NOTICE: 可能你的 `${HOME}/.local/bin/` 目录还不在环境变量 `PATH` 里, 需要将其加入 `PATH` 才能找到这些命令

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

**自己重新划分数据集**

> DEPRECATED: 这个部分已经Deprecated，还是使用涛宝宝之前划分的数据

由于据说2013的bbox `train` 数据标注的不好, 所以准备只用2014新增的 `train` 数据和2012 ～ 2013的 `val` 数据划分成新的 `train` 和 `val` 集合.

> NOTICE: 以下用到的脚本都在 scripts 目录下

1. (*由于每次生成有随机性，数据不同. 为了训练网络的时候方便对比, 大家先都用当前 `scripts/cross/*.txt` 的这三个文件. 不用做第一步了*) 运行命令
   ```
   python generate_training_subset.py -s 'range(1, 201)' -o train_10_fold.txt -v val_10_fold.txt -p 0.9 -a ${ILSVRC_DEVKIT_DIR}/data/det_lists/val.txt -b ${IMAGENET_DATA_DIR}/ILSVRC2013_DET_val/
   ```
2. 使用 `val.ValAPI` 测试和使用ILSVRC的matlab mAP evaluate例程计算mAP的时候, 需要传的 `val.txt` 比上面生成的 `val_10_fold.txt` 要加一个 1-based 的index. 而且还是相对于 `${IMAGENET_DATA_DIR}/ILSVRC2013_DET_[bbox]_val/` 这个目录的相对路径, 而且还只有一层... 需要做一个目录里面放了软链接到对应的那些JPEG(提供给`val.ValAPI`)/xml(提供给`eval_det.m`)文件. 运行: `python prepare_val_dir.py val_10_fold.txt </path/to/your/own/val/image/path> </path/to/your/own/val/gt/path>`
4. 创建完上面那个目录后, 运行以下命令生成供 `val.ValAPI` 和 `eval_det.m` 使用的 `val.txt`
   ```
   awk -F'/' '{printf "%s %s\n", $NF, NR}' val_10_fold.txt >val.txt
   ```

跑的过程中发现有一些图像对应的bbox的标注是错的, 比如标注文件 `ILSVRC2014_DET_bbox_train/ILSVRC2014_train_0006/ILSVRC2014_train_00060036.xml` 出现 `xmin > xmax` 的情况:

```xml
        <object>
                <name>n00007846</name>
                <bndbox>
                        <xmin>1</xmin>
                        <xmax>0</xmax>
                        <ymin>498</ymin>
                        <ymax>498</ymax>
                </bndbox>
        </object>
```

现在直接把这些图像文件(.JPEG)的相对 `${IMAGENET_DATA_DIR}` 的路径暂时放在 `scripts/cross/train.blacklist` 里面, 等待删除

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

### Http server

**client端**
Http Server的配置在lpirc.config中的httpapi中进行配置，各选项都有注释，目前的用户名有lpirc, jiantao, woinck, foxfi, 其中lpirc的密码为pass，其他密码均与用户名同。

当测试数据较多时，若在tx1上进行http server的测试，为存储空间考虑，请在config中将del_img设置为true。

**server端**
server的官方repo[在这里](https://github.com/luyunghsiang/LPIRC)，另外，现在在jiantao.eva2.nics.cc上长期运行着一个http server，程序位置为*/home/woinck/proj/LPIRC/* (记为SERVER_DIR)，启动位置为SERVER_DIR/server/source/startserver.sh，若需要添加新用户则可以在referee.py中添加

服务器将client提交的数据存在SERVER_DIR/csv/tmp/your_user_name.csv中，每个bounding box为一行，分别为图片编号，class_id，置信度，bounding box的四个坐标。

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

### Helpers

`scripts`文件夹下有一些帮助训练和测试的脚本, 都很简单, 不一定要用, 自己写scripts也行. Anyway, FYI:

* draw_net.py: `python draw_net.py <prototxt文件名> <生成的图片路径>.png` 可视化网络结构. `python draw_net.py <包含prototxt的文件夹> <存放生成图片的文件夹名>` 可递归画出一个文件夹下后缀名`.pt`或者`.prototxt`结尾的网络.

> NOTICE: 某些脚本有一些依赖包, 可能需要 `pip install -r requirements.txt --user`
