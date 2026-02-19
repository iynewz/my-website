---
tags:
  - OSTEP
  - Scheduling
  - Concurrency
---

# 10. Multiprocessor Scheduling (Advanced)

前一章介绍的 Lottery scheduling 和 Stride scheduling 原始设计是为了单处理器服务的。在多核 CPU 上，如何调度？
单核和多核最大的区别是，对缓存和内存的使用。多核 CPU 系统中，每个核通常有自己的 L1/L2 缓存，同时可能有共享的 L3 缓存。

## cache coherence 缓存一致性问题

问题描述：当多个核缓存了同一块内存的数据时，如果一个核修改了数据，而其他核的缓存没有同步更新，就会出现"数据不一致"的问题。

解决方法是用总线监听 + MESI 协议。**MESI** 描述每个缓存行在 CPU 缓存中只能有 4 种状态：Modified, Exclusive, Shared, Invalid. 每个 CPU 缓存监听（snoop）总线上其他 CPU 的读/写请求，当发现自己缓存中的行被其他 CPU 访问时，根据 MESI 作出反应。这个协议可以保证当一个核修改数据，其他核的缓存要么更新，要么标记为无效，各 CPU 看到的内存值是一致的。

这时候为什么不使用锁？锁可以保护共享内存，但无法保证**缓存一致性。** 如果没有缓存一致性，同步原语无法保证正确性。同步原语依赖于缓存一致性。

如果反过来：如果没有锁，只有缓存一致性，并发操作的数据结构仍然会损坏。

## 缓存亲和度 Cache Affinity

如果一个线程长期运行在 CPU Core 3 ，L1/L2 cache 里有它的热数据，分支预测器状态是训练好的；TLB 也已经 warm。一旦被调度到 Core 7，cache miss 暴涨，TLB 重新填充，latency spike。

在上述背景下，如何设计 Scheduling？

1.  单队列循环，任务都放在同一个队列里

    ![](https://dv1bxe6i68b.feishu.cn/space/api/box/stream/download/asynccode/?code=NjAzNmRmMWY3YTc0ZTJlZDBlMDA4OWE1ODVjMGUwODFfWVgyTVhUYlFGam9wNEpMdEpLQlc2bVg2QjJpbnZ1SmJfVG9rZW46SjVCN2JLYUg1bzRKMmt4TkttdmNBZk15bnRmXzE3NzE1MDU2NzQ6MTc3MTUwOTI3NF9WNA)

    单队列时，一个工作进入一个CPU，为了防止其他 CPU 对这个工作进行操作，要对其加锁，产生开销。

    但是，简单的单队列设计破坏了 Cache Affinity（如上图）

2.  多队列循环

    有多个调度队列，每个队列使用不同的调度规则。

    可能出现调度不均的问题。解决方法是 job migration，通过工作的跨 CPU 迁移 (**Work stealing**)，可以真正实现负载均衡。