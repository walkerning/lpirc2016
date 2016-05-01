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
