---
tags:
  - OSTEP
  - Locks
  - Concurrency
---

# 32. Common Concurrency Problems

常见并发问题有哪些？如何避免？

## 非死锁的缺陷

绝大多数的非死锁的缺陷都和互斥和同步有关：

1. （互斥）违反原子性错误：对临界区的 access 必须是原子性的。可以给临界区加锁来保证原子性。

2. （同步）违反顺序错误：两个内存位置预期应该按一定顺序访问，比如一个变量应该先初始化再引用，否则会引用空指针。为了保证执行按照一定顺序，可以用条件变量或信号量来解决。

## 死锁缺陷

死锁四个条件里，破除一个就可以不产生死锁。🤔 那为什么还会写出死锁呢……？因为实际工程的代码会不断演化、互相依赖。

操作系统里最经典的死锁来源之一是：虚拟内存系统需要把页面从磁盘换入；文件系统读磁盘，需要一个 buffer，buffer 在内存里，内存可能需要分配新页。于是有可能产生互相依赖：

VM 持有 VM 锁 → 请求 FS

FS 持有 FS 锁 → 请求 VM

而且真实的工程代码，会封装细节，看起来无关的接口可能会导致死锁。

## 死锁四个条件

见 [CSAPP/Concurrent Programming](https://iynewz.dev/csapp/12/#deadlock)

## 预防死锁的细节

### 通过破坏 Circular Wait 条件

用 total ordering 或 partial ordering 来控制获取锁的顺序，并要求所有线程按该顺序获取锁，可以消除 circular wait。具体实现中，可以使用锁地址作为排序键（因为每个 mutex 在内存里都有唯一地址），规定每个线程只能从高地址 往 低地址拿锁。

### 通过破坏 Hold-and-Wait 条件

解决方法是在拿任何“普通锁”之前，先拿一个全局的“锁获取锁”，相当于一次性把所有的锁全拿了，这样其他线程不会在中途插一脚。

```c
pthread_mutex_lock(prevention); // begin acquisition
pthread_mutex_lock(L1);
pthread_mutex_lock(L2);
...
pthread_mutex_unlock(prevention); // e
```

但这个方法问题很多，破坏了封装性、显著降低并发度，并在工程实践中用得很少。

### 通过允许抢占（No Preemption 的反面）

```c
top:
pthread_mutex_lock(L1);
if (pthread_mutex_trylock(L2) != 0) {
    pthread_mutex_unlock(L1);
    goto top;
}
```

trylock 不阻塞，失败就主动 unlock(L1) ，这样线程不可能在“持有一个锁的同时阻塞等待另一个锁”。

但这会引发 Livelock（活锁） 的问题，也就是互相礼让对方同样有可能陷入僵局。

### 破坏 Mutual Exclusion

```c
int CompareAndSwap(int *address, int expected, int new) {
    if (*address == expected) {
        *address = new;
        return 1; // 成功
    }
    return 0; // 失败
}
```
用 CAS 可以实现原子更新，不需要显式加锁。都无锁了，就不可能发生死锁。但硬件支持不是什么情况都能满足的。

## 用动态调度避免死锁

之前讲的是破坏四个死锁条件之一来预防死锁，还可以通过动态调度，保证系统不会进入不安全状态。

如果能提前知道每个线程可能会获取哪些锁，那么可以通过调度来安排。

谁来控制调度器？程序员可以在小规模、静态、受控环境下提前写调度器，实现死锁避免。但在通用操作系统和大规模多线程程序里，程序员也无法完全控制调度器，因此这种方法很少用于实际应用。

## Detect and Recover
最后一种策略是允许偶尔有 deadlock，等发生了再采取行动。这也是一种成本和损失的 tradeoff。