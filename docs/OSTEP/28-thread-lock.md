---
tags:
  - OSTEP
  - Locks
  - Concurrency
---

# 28. Locks

在系统层面，锁是一种用于协调并发访问的共享资源；在语言/实现层面，锁通常表现为一个或一组共享变量。

评价锁的三个方面：

1. mutual exclusion：保证互斥
   
2. fairness：保证不存在无限期等待的线程，即不会发生饥饿（starvation）；理想情况下，等待时间是有界的。
   
3. performance：无竞争、轻度竞争、重度竞争时，锁的效率如何

## 如何实现锁？

这一章讲的是锁在真实情况下锁是如何实现的：需要一些硬件上更强大的指令，和一些操作系统所支持的原语。

首先，mutual exclusion 是怎么保证的？靠的就是「关中断」和「原子硬件指令」。

**尝试 1: OS 层面的关闭中断 Turning off Interrupts**

一种最早期的互斥实现思路是在操作系统内核中临时关闭中断（就是是四种异常之一的那个中断）。

通过在进入临界区前关闭中断，在退出临界区后重新开启中断，可以保证当前执行流在临界区内不被抢占，从而在表面上实现原子性。

turn off interrupts 是谁做的？谁有权限让 cpu 都不 interrupt？

关闭中断用的 DisableInterrupts() / EnableInterrupts() 不是普通函数，它们是内核函数，最终会执行 CPU 的特权指令，用户态程序无法直接关闭中断，只有操作系统内核可以调用。

这个做法的缺点很多：

1. 恶意程序 DisableInterrupts 后不 Enable，独占 cpu
   
2. 多核 cpu 的问题。中断是每个 CPU 核私有的。线程的栈只保护“局部变量”，只要不是栈上的东西，默认都是共享的。核 a 关闭中断了，其他核 b 上的线程还是可以 access 共享数据。
   
3. 最主要的问题，中断的丢失可导致操作系统严重的错误。比如关闭中断期间，如果设备发出中断请求，中断信号可能被忽略而非排队。

由于上述问题，通过关闭中断实现锁仅在极其有限的内核场景中使用。

**尝试 2: 软件层面的锁**

关闭中断的方法无法在多处理器上工作，所以系统设计者开始希望造出「锁」。

一种尝试是：（反例）

```c
typedef struct __lock_t {
    int flag;   // 0 -> lock is free, 1 -> lock is held
} lock_t;

void init(lock_t *mutex) {
    mutex->flag = 0;
}

void lock(lock_t *mutex) {
    while (mutex->flag == 1) // #10
        ;               // #11 busy waiting (spin)
    mutex->flag = 1;    // #12 acquire the lock
}

void unlock(lock_t *mutex) {
    mutex->flag = 0;
}
```

乍一看是对的，但问题是，这个锁不是原子的。在 lock 内部，第 10 行 while 语句读内存（load），12 行写内存（store），这两个操作不是原子的。

假设初始状态：mutex->flag = 0，有可能发生：

![alt text](image-4.png)

两个线程都 set flag=1, 拿到锁并进入临界区，没有实现正确的互斥。（更不用说 spin 的性能问题了）

(我对这个错误实现的理解是：想要用锁来保护临界区，但是锁自己却变成了临界区。)

锁的互斥，靠普通的“先读再写”的软件是无法实现的，只能依赖于**硬件提供的原子操作原语（atomic primitives）**，这是并发控制的基础。


## 硬件原语（atomic primitives）解决方案

### Test-And-Set

Test-and-Set 是一种由硬件提供的原子「读-改-写」操作原语。

它将对锁变量的“读取旧值（test）”和“写入新值（set）”合并为一个不可分割的原子操作，从而保证在并发执行环境中，至多只有一个线程能够成功将锁从未占用状态转换为占用状态。

在多核系统中，CPU 在执行 Test-and-Set 时，会通过缓存一致性协议（或早期系统中的总线锁定机制）独占目标内存地址所在的缓存行的修改权限，从硬件层面防止其他处理器同时观察或修改该内存位置，进而保证操作的原子性与全局可见性。

在 x86, Test-and-Set 的实现是靠 xchg 指令。

```c
void lock(lock_t *l) {
    while (TestAndSet(&l->flag) == 1)
        ; // spin
}
```



### Compare-And-Swap

Compare-And-Swap 也是是一种由硬件提供的原子「读-改-写」操作原语。

把“1. 从内存地址中读取旧值（old） 2. 将该旧值与期望值（expected）进行比较 3. 若相等，则将内存中的值更新为新值（new）”合并为一个不可分割的原子操作。

```c
void lock(lock_t *l) {
    while (!CompareAndSwap(&l->flag, 0, 1)) //只有当锁当前是 0 时，才把它设为 1
        ; // spin
}
```

在 x86, CAS 的实现是靠 cmpxchg 指令。（单独有一个硬件指令）
CAS 比 TAS 强大一些，更适合复杂并发结构。


### Load-Linked and Store-Conditional

### Fetch-And-Add

```c
typedef struct __lock_t {
    int ticket; // 下一个可发放的票号
    int turn; // 当前正在服务的票号，谁的票号 == turn，谁就能进临界区
} lock_t;

void lock_init(lock_t *lock) {
    lock->ticket = 0;
    lock->turn = 0;
}

void lock(lock_t *lock) {
    int myturn = FetchAndAdd(&lock->ticket);
    while (lock->turn != myturn)
        ; // spin
}

void unlock(lock_t *lock) {
    lock->turn = lock->turn + 1;
}
```

Ticket lock 使用原子 FetchAndAdd 分配唯一票号，线程按票号顺序自旋等待 turn，解锁时递增 turn，从而实现公平的自旋锁。

### run-and-yield

这个方法的思想是，如一个线程在获取锁的时候发现锁被其他线程抢占，与其自旋，不如把 CPU 的控制权交出去。假设 100 个线程，有一个线程一直占锁，其他 99 个线程都 run-and-yield, 这会带来巨大的 context switch 的开销（虽然比纯自旋带来的开销小一点）。

run-and-yield 把自旋成本换成了调度成本。更糟糕的是如果调度器策略不公平，某个线程不停地 yield, 最终会饿死（无法向前推进）。

（这也是为什么 OS 要提供接下来介绍的阻塞原语，让失败线程直接睡眠，不再参与调度）。

### Using Queues

之前的方法，要么是让线程自旋，要么是让线程立即 yield。如果操作系统的调度策略不够好，都可能会带来巨大开销和饿死的问题。所以我们需要操作系统的帮助，也需要维护一个队列，知道哪些 thread 正在等待获取锁。

Solaris 是一个像 linux 一样独立的 OS，Solaris 是最早将 park/ unpark 这种机制广泛应用于线程同步的操作系统。

park()：阻塞当前线程，让它挂起，直到被其他线程唤醒或操作系统中断。

unpark(thread)：唤醒被 park 阻塞的线程。

只要线程不在就绪队列里，CPU 就不会运行它。

```c
typedef struct __lock_t {
    int flag;      // 0: free, 1: held
    int guard;     // spinlock to protect this structure
    queue_t *q;    // waiting threads
} lock_t;

void lock(lock_t *m) {
    while (TestAndSet(&m->guard, 1) == 1)
        ; //acquire guard lock by spinning
    if (m->flag == 0) { 
        m->flag = 1; // 锁空闲的情况，拿到锁
        m->guard = 0;
    } else { // 锁被占用的情况
        queue_add(m->q, gettid()); // 把自己加入等待队列
        m->guard = 0;
        park();
    }
}

void unlock(lock_t *m) {
    while (TestAndSet(&m->guard, 1) == 1)
        ; // spin
    if (queue_empty(m->q)) {
        m->flag = 0; // 没人等，直接释放锁
    } else { 
        // 有人等，唤醒一个
        int tid = queue_remove(m->q);
        unpark(tid);
        // 注意：flag 仍然是 1，锁的“所有权”被直接转交
    }

    m->guard = 0;
}
```

（回忆一下，TestAndSet 返回的是旧值，返回 0 说明成功拿到了 guard; 返回 1 说明 guard 原来就被别人拿着。）

guard 是一个「保护锁的锁」，用来保护锁的两个原数据： flag（锁是否被占用） 和 queue （拿不到锁的等待线程）。每把锁有自己独立的 guard.

获取 guard 的部分仍然是自旋的。这个方法没有完全的避免自旋，但已经把 spin 压缩到了一个更小的范围。

如果当前 thread 没有拿到 flag 锁，做三件事：

```c
queue_add(m->q, gettid()) // 1. 把自己加入等待队列
m->guard = 0; // 2. 设置 guard 为 0
park(); // 3. 睡眠
```

注意 2 和 3 这俩顺序不能反。原因是？Park 让线程睡眠。如果线程 1 先 park 了，它在睡眠时仍然持有 guard, 那其他的想拿同一把锁的线程 2 就永远拿不到 guard 了。（但是如果线程3 想拿其他锁，还是不影响的）

**wakeup race**

仍然有个问题：比如线程 1 已经将自己加入 wait 的队列了，但是还没有完成 park()，如果这时候发生中断，另一个线程 unlock()，从等待队列里取出了线程 1，那么线程 1 继续执行的是 park(), 就长眠不醒了！

也就是说 guard 无法保护好 park 这种线程状态转换的东西。

（park 实际发生了什么？用户态 → 内核态？内核还有一个 queue）

Solaris 的做法是在 park 之前再加一个 「我马上要 park」的 setpark() 系统调用。

还有一种做法是把 guard 传进内核，让锁变成原子的，就不会出现 race condition 了。

### priority inversion & spinlock

自旋锁和优先级组合在一起，会永远自旋的例子：

高优先级线程一旦自旋了，低优先级、持锁线程永远挤出 CPU。