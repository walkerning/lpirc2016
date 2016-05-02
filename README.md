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
- [ ] profiling, 方便之后做各种参数的选择

