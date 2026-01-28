---
tags:
  - OSTEP
  - Locks
  - Concurrency
---
# 32. Locked Data Structures

在并发程序中，如何在保证正确性的前提下，尽可能提高并发性能？

本章通过对不同数据结构（如计数器、链表、队列、哈希表）的加锁方式进行对比，说明了并发性能不仅取决于锁本身，更取决于数据结构和算法的设计方式。

## 并发计数器

计数器一般用于统计请求数，统计任务完成数，引用计数等任务。在多线程环境中，计数器是多个线程共享的变量，因此对它的操作必须是线程安全的。

Precise Counter

最直接的实现是一个 Precise Counter：

```c
typedef struct __counter_t {
    int value;
    pthread_mutex_t lock;
} counter_t;

void init(counter_t *c) {
    c->value = 0;
    Pthread_mutex_init(&c->lock, NULL);
}

void increment(counter_t *c) {
    Pthread_mutex_lock(&c->lock);
    c->value++;
    Pthread_mutex_unlock(&c->lock);
}

void decrement(counter_t *c) {
    Pthread_mutex_lock(&c->lock);
    c->value--;
    Pthread_mutex_unlock(&c->lock);
}

int get(counter_t *c) {
    Pthread_mutex_lock(&c->lock);
    int rc = c->value;
    Pthread_mutex_unlock(&c->lock);
    return rc;
}
```

所有对 value 的访问都被同一把互斥锁保护，每一次操作都加锁。

尽管该实现逻辑上完全正确，但它在并发场景下，性能如何呢？

--
  为了定量测试不同锁的实现的性能，需要 benchmark。规则是：
  有 N 个线程，所有线程共享一个计数器，每个线程对该计数器执行固定次数的更新操作（如 increment），测量程序完成的总时间。逐步增加线程数 N，观察性能变化
  最优情况是 perfect scaling：
  1 个线程 在 1 个处理器上完成任务需要时间 T
  N 个线程 在 N 个处理器上完成等量任务，仍然只需要 T
  这种情况是最优的。
--