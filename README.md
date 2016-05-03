LPIRC 2016
================

Arch
----------------

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


Config
----------------

`lpirc.conf.sample`里是一个示例配置文件


TODO
----------------

- [ ] HTTP api实现
- [ ] 可视化脚本
- [ ] profiling, 方便之后做各种参数的选择

Problems
----------------

如果是调用caffe的c++过程们中间出错退出, 不能在Python的`atexit`和`except:`里面抓到, 导致子进程不能被安全的退出。应该要开两个进程，另一个进程负责管理. 不过感觉对于正确情况没必要, 所以不实现了