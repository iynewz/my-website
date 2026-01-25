---
tags:
  - OSTEP
  - Locks
  - Concurrency
---

# 33. Event-based Concurrency (Advanced)

并发不一定要通过多线程来实现。还有一种模式是 event-based concurrency （事件驱动并发）。现代的 server-side 框架 Node.js 就使用了这种模式。

基于事件的并发系统，和基于线程的并发系统，有哪些不同？

## Eventloop

Eventloop 是一个基于事件的并发系统模型：

```c
while(1) {
    events = getEvents();
    for (e in Events) {
        processEvent(e);
    }
}
```


有两个重点：

1. 基于事件的系统被设计成单线程的，因为是单线程的，不会有两个 JS 线程同时访问同一个内存变量，也不需要锁了。

2. Event control 决定下一步做哪个事件，就相当于在「基于线程的并发系统里，操作系统对线程的调度」。但操作系统的调度是用户层控制不了的，在事件调度里，用户是可以细粒度控制的。

## Receive Events API: select() 和 poll()

在基于事件的服务器里，服务器如何确定是否有他的消息已经到达？（比如 socket / 文件描述符上有没有可读、可写、异常事件）

用的是 select() 和 poll() 去轮询（或者等待）这些文件描述符。

Select 可见：https://iynewz.dev/csapp/12/#select

Select，poll 是 I/O primitive 。（之前学到，锁和信号量是同步 primitive。primitive 是不可分解的操作或工具。）

select / poll / epoll 是 I/O multiplexing 的方法。multiplexing 指的是一个资源服务多个对象，所以叫「复用」。线程资源只有一个，但 fd 有多个，一个线程可以同时等待多个 I/O 对象的事件，叫做 I/O multiplexing.

## 可以不轮询的方法：异步 I/O

如果一个事件处理程序发出了一个阻塞的调用，那么整个系统都会阻塞。所以基于事件的并发系统，必须遵守一个规则，就是不允许阻塞调用。（比如事件并发系统里一个线程 busy spin, sleep 是不允许的）。那怎么处理一个可能阻塞的 systemcall 呢？（比如 read()？）

为了解决事件驱动系统里的等待，引入异步（asynchronous） I/O 。

同步和异步是正交概念。阻塞是同步的，阻塞接口在返回给调用者之前完成所有工作；阻塞的反义词是异步，异步接口立即返回，让所有需要完成的工作在后台完成，即由内核在 I/O 完成后通知用户程序

example：

调用异步 io (aio_read)之后，aio_read 立即返回，这样可以继续执行下一个事件。

如何得知异步 io 是否完成？有以下几种方法：

1. 通过 aio_error 轮询，这其实还是用户态轮询，看起来又像 select 了。

2. 真正的“内核通知”：用 UNIX signals，真正不需要轮询了，而是异步 IO 完成时内核主动打断 (interrupt) 程序。

补充：什么是 UNIX SIGNAL

是不是就是 syscall? 不是。syscall 是系统调用由用户程序主动发起的，signal 是内核向用户进程传递异步事件的一种机制。

## State Management

在现代多核系统中，事件处理往往分布在多个 CPU 或线程上，导致共享状态被并发访问，从而引入竞态条件，使得简单的无锁事件处理不再可行。

而且，paging 和 event-based 并发会产生冲突。Paging 是把内存当成“会被操作系统随时收走/换走”的资源。Paging 的工作机制是，程序看到的是虚拟地址空间，当程序访问某个虚拟地址时，CPU 查页表，如果发现这个页不在内存里，会触发 page fault。这个时候内核介入，从磁盘把页读回来，更新页表，再重新执行那条指令。从系统视角看这就是一次磁盘 I/O，而且这个 I/O 是可能很慢。但 event loop的核心假设是事件处理函数 handler 必须 不阻塞的。

其实读到这里更理解为什么要有 thread pool 了。在 event + thread pool 方案里，event loop 只做：accept，epoll，分发任务；真正可能 page fault 的工作让 worker threads 来做。
