---
comments: true
tags:
  - OSTEP
  - Concurrency
---

# homework-27

[README](https://github.com/remzi-arpacidusseau/ostep-homework/blob/master/threads-api/README.md)

Valgrind 是一个运行时工具。它在自己的执行引擎下运行程序，并允许不同的工具检查程序的内存使用、线程行为以及性能。

Valgrind 对软件正确性工具的发展产生了巨大影响，被广泛用于内存调试和性能分析，尤其是在 C/C++ 程序中。AddressSanitizer（ASan）很可能就是受到了 Valgrind 的启发。

Helgrind 是 Valgrind 里的一个插件，用于检测使用 POSIX pthreads 线程原语的 C、C++ 和 Fortran 程序中的同步错误。  

## Question 1

看下源代码：

```c
#include <stdio.h>

#include "common_threads.h"

int balance = 0;

void* worker(void* arg) {
    balance++; // unprotected access 
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t p;
    Pthread_create(&p, NULL, worker, NULL);
    balance++; // unprotected access
    Pthread_join(p, NULL);
    return 0;
}
```

程序一开始只有 main() 一个线程，`Pthread_create()` 创建了一个新线程 p，p 开始执行 `worker()`。此时，两个线程并发执行。这两个线程都对共享变量 balance 执行了增加操作，而且没有锁来保护临界区，可能发生 data race. 

main() 执行到 `Pthread_join()`，阻塞当前调用者线程 main()，直到线程 p 结束。但，这个时候阻塞也没有意义，之前已经两个线程并发操作共享变量了。

编译 main-race.c:

```
make
gcc -g -pthread main-race.c -o main-race
```

POSIX 线程是 OS / libc 提供的能力，需要用 `-pthread` 明确让编译器启用并对接这套线程模型。

看一下 helgrind 报告：`valgrind --tool=helgrind ./main-race`

```
==1675248== Helgrind, a thread error detector
==1675248== Copyright (C) 2007-2017, and GNU GPL'd, by OpenWorks LLP et al.
==1675248== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==1675248== Command: ./main-race
==1675248== 
==1675248== ---Thread-Announcement------------------------------------------
==1675248== 
==1675248== Thread #1 is the program's root thread
==1675248== 
==1675248== ---Thread-Announcement------------------------------------------
==1675248== 
==1675248== Thread #2 was created
==1675248==    at 0x498F9F3: clone (clone.S:76)
==1675248==    by 0x49908EE: __clone_internal (clone-internal.c:83)
==1675248==    by 0x48FE6D8: create_thread (pthread_create.c:295)
==1675248==    by 0x48FF1FF: pthread_create@@GLIBC_2.34 (pthread_create.c:828)
==1675248==    by 0x4853767: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==1675248==    by 0x109209: main (main-race.c:14)
==1675248== 
==1675248== ----------------------------------------------------------------
==1675248== 
==1675248== Possible data race during read of size 4 at 0x10C014 by thread #1
==1675248== Locks held: none
==1675248==    at 0x109236: main (main-race.c:15)
==1675248== 
==1675248== This conflicts with a previous write of size 4 by thread #2
==1675248== Locks held: none
==1675248==    at 0x1091BE: worker (main-race.c:8)
==1675248==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==1675248==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==1675248==    by 0x498FA03: clone (clone.S:100)
==1675248==  Address 0x10c014 is 0 bytes inside data symbol "balance"
==1675248== 
==1675248== ----------------------------------------------------------------
==1675248== 
==1675248== Possible data race during write of size 4 at 0x10C014 by thread #1
==1675248== Locks held: none
==1675248==    at 0x10923F: main (main-race.c:15)
==1675248== 
==1675248== This conflicts with a previous write of size 4 by thread #2
==1675248== Locks held: none
==1675248==    at 0x1091BE: worker (main-race.c:8)
==1675248==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==1675248==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==1675248==    by 0x498FA03: clone (clone.S:100)
==1675248==  Address 0x10c014 is 0 bytes inside data symbol "balance"
==1675248== 
==1675248== 
==1675248== Use --history-level=approx or =none to gain increased speed, at
==1675248== the cost of reduced accuracy of conflicting-access information
==1675248== For lists of detected and suppressed errors, rerun with: -s
==1675248== ERROR SUMMARY: 2 errors from 2 contexts (suppressed: 0 from 0)
```

指出了 Possible data race 及其位置，以及 inside data symbol "balance"。

两个线程都可以访问 balance ，但不持有任何锁。冲突的地方分别是第 15 行（main）和第 8 行（worker）的 read 和 write。

## Question 2

第一种情况：删除其中一条 balance++, 预期应该没有 data race 了。重新编译运行试了一下，果然：`ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)`

第二种情况：只给其中一个更新加锁。比如在 main 里加锁：

```c
#include <stdio.h>
#include "common_threads.h"

int balance = 0;
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;

void *worker(void *arg) {
    balance++;          // 没加锁
    return NULL;
}

int main() {
    pthread_t p;
    pthread_create(&p, NULL, worker, NULL);
    pthread_mutex_lock(&m);
    balance++;          // 加锁
    pthread_mutex_unlock(&m);
    pthread_join(p, NULL);
    return 0;
}
```

mutex 保证同一时间内，只有一个线程可以进入锁保护的临界区。main 里的 mutex 保证了在这段锁保护的区域内的操作，对于**持同一把锁的其他线程**是互斥的。锁只约束使用它的线程。worker 不受 mutex 的约束，data race 完全有可能发生。main 里单独的加锁，并不会让 balance++ 成为“原子操作”

```
T1 (main thread):               T2 (worker thread):
----------------------------------------------------------
pthread_create

lock(m)
load balance = 0
                               load balance = 0   // data race
add 1  -> 1
                               add 1 -> 1
store balance = 1
                               store balance = 1   // 覆盖
unlock(m)

pthread_join
```

在 helgrind 报告里，可以看到锁相关的信息：

```
==1695679==  Lock at 0x10C060 was first observed
==1695679==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==1695679==    by 0x109231: main (main-race.c:16)
==1695679==  Address 0x10c060 is 0 bytes inside data symbol "m"
==1695679== 
==1695679== Possible data race during write of size 4 at 0x10C040 by thread #1
==1695679== Locks held: 1, at address 0x10C060
==1695679==    at 0x10923B: main (main-race.c:17)
==1695679== 
==1695679== This conflicts with a previous write of size 4 by thread #2
==1695679== Locks held: none
==1695679==    at 0x1091DE: worker (main-race.c:9)
==1695679==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==1695679==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==1695679==    by 0x498FA03: clone (clone.S:100)
==1695679==  Address 0x10c040 is 0 bytes inside data symbol "balance"
```

main 持有锁，worker 没有锁，可能发生 data race.

修复方式是让所有线程都加锁：

```
void *worker(void *arg) {
    pthread_mutex_lock(&m);
    balance++;
    pthread_mutex_unlock(&m);
    return NULL;
}
```

```
==3609035== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 7 from 7)
```

不错，可以通过了！

## Question 3, 4

```c
#include <stdio.h>

#include "common_threads.h"

pthread_mutex_t m1 = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t m2 = PTHREAD_MUTEX_INITIALIZER;

void* worker(void* arg) {
    if ((long long) arg == 0) {
	Pthread_mutex_lock(&m1);
	Pthread_mutex_lock(&m2);
    } else {
	Pthread_mutex_lock(&m2);
	Pthread_mutex_lock(&m1);
    }
    Pthread_mutex_unlock(&m1);
    Pthread_mutex_unlock(&m2);
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t p1, p2;
    Pthread_create(&p1, NULL, worker, (void *) (long long) 0);
    Pthread_create(&p2, NULL, worker, (void *) (long long) 1);
    Pthread_join(p1, NULL);
    Pthread_join(p2, NULL);
    return 0;
}
```

回忆一下，[Pthread_create](./27-thread-api.md) 的第四个参数是第三个参数的参数。p1 会依次拿 m1, m2; p2 会依次拿 lock m2, m1.

这个情况是**可能**发生死锁的。如果 p1 拿 m1 时，p2 刚好拿 m2，就形成循环等待，死锁发生。

(而不是一定发生死锁？可能 p1 先执行完成，unlock 了 m1, m2, p2 再继续顺利拿锁。)

Valgrind 结果是

```
==3614068== ---Thread-Announcement------------------------------------------
==3614068== 
==3614068== Thread #3 was created
==3614068==    at 0x498F9F3: clone (clone.S:76)
==3614068==    by 0x49908EE: __clone_internal (clone-internal.c:83)
==3614068==    by 0x48FE6D8: create_thread (pthread_create.c:295)
==3614068==    by 0x48FF1FF: pthread_create@@GLIBC_2.34 (pthread_create.c:828)
==3614068==    by 0x4853767: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x1093F4: main (main-deadlock.c:24)
==3614068== 
==3614068== ----------------------------------------------------------------
==3614068== 
==3614068== Thread #3: lock order "0x10C040 before 0x10C080" violated
==3614068== 
==3614068== Observed (incorrect) order is: acquisition of lock at 0x10C080
==3614068==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x109288: worker (main-deadlock.c:13)
==3614068==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3614068==    by 0x498FA03: clone (clone.S:100)
==3614068== 
==3614068==  followed by a later acquisition of lock at 0x10C040
==3614068==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x1092C3: worker (main-deadlock.c:14)
==3614068==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3614068==    by 0x498FA03: clone (clone.S:100)
==3614068== 
==3614068== Required order was established by acquisition of lock at 0x10C040
==3614068==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x10920E: worker (main-deadlock.c:10)
==3614068==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3614068==    by 0x498FA03: clone (clone.S:100)
==3614068== 
==3614068==  followed by a later acquisition of lock at 0x10C080
==3614068==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x109249: worker (main-deadlock.c:11)
==3614068==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3614068==    by 0x498FA03: clone (clone.S:100)
==3614068== 
==3614068==  Lock at 0x10C040 was first observed
==3614068==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x10920E: worker (main-deadlock.c:10)
==3614068==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3614068==    by 0x498FA03: clone (clone.S:100)
==3614068==  Address 0x10c040 is 0 bytes inside data symbol "m1"
==3614068== 
==3614068==  Lock at 0x10C080 was first observed
==3614068==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x109249: worker (main-deadlock.c:11)
==3614068==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3614068==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3614068==    by 0x498FA03: clone (clone.S:100)
==3614068==  Address 0x10c080 is 0 bytes inside data symbol "m2"
==3614068== 
==3614068== 
==3614068== 
==3614068== Use --history-level=approx or =none to gain increased speed, at
==3614068== the cost of reduced accuracy of conflicting-access information
==3614068== For lists of detected and suppressed errors, rerun with: -s
==3614068== ERROR SUMMARY: 1 errors from 1 contexts (suppressed: 7 from 7)
```

## Question 5

在 worker 里添加一把 global lock;

```c
void* worker(void* arg) {
    Pthread_mutex_lock(&g); // 添加一把锁
    if ((long long) arg == 0) {
	Pthread_mutex_lock(&m1);
	Pthread_mutex_lock(&m2);
    } else {
	Pthread_mutex_lock(&m2);
	Pthread_mutex_lock(&m1);
    }
    Pthread_mutex_unlock(&m1);
    Pthread_mutex_unlock(&m2);
    Pthread_mutex_unlock(&g);
    return NULL;
}
```

这起到了什么效果？如果一个 thread 没有拿到 g, 那么它就不继续执行 if, 也不试着获取 m1 或 m2. 这让 m1 和 m2 必须一起拿走。

```
==3649251== Helgrind, a thread error detector
==3649251== Copyright (C) 2007-2017, and GNU GPL'd, by OpenWorks LLP et al.
==3649251== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==3649251== Command: ./main-deadlock-global
==3649251== 
==3649251== ---Thread-Announcement------------------------------------------
==3649251== 
==3649251== Thread #3 was created
==3649251==    at 0x498F9F3: clone (clone.S:76)
==3649251==    by 0x49908EE: __clone_internal (clone-internal.c:83)
==3649251==    by 0x48FE6D8: create_thread (pthread_create.c:295)
==3649251==    by 0x48FF1FF: pthread_create@@GLIBC_2.34 (pthread_create.c:828)
==3649251==    by 0x4853767: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x10946A: main (main-deadlock-global.c:27)
==3649251== 
==3649251== ----------------------------------------------------------------
==3649251== 
==3649251== Thread #3: lock order "0x10C080 before 0x10C0C0" violated
==3649251== 
==3649251== Observed (incorrect) order is: acquisition of lock at 0x10C0C0
==3649251==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x1092C3: worker (main-deadlock-global.c:15)
==3649251==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3649251==    by 0x498FA03: clone (clone.S:100)
==3649251== 
==3649251==  followed by a later acquisition of lock at 0x10C080
==3649251==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x1092FE: worker (main-deadlock-global.c:16)
==3649251==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3649251==    by 0x498FA03: clone (clone.S:100)
==3649251== 
==3649251== Required order was established by acquisition of lock at 0x10C080
==3649251==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x109249: worker (main-deadlock-global.c:12)
==3649251==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3649251==    by 0x498FA03: clone (clone.S:100)
==3649251== 
==3649251==  followed by a later acquisition of lock at 0x10C0C0
==3649251==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x109284: worker (main-deadlock-global.c:13)
==3649251==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3649251==    by 0x498FA03: clone (clone.S:100)
==3649251== 
==3649251==  Lock at 0x10C080 was first observed
==3649251==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x109249: worker (main-deadlock-global.c:12)
==3649251==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3649251==    by 0x498FA03: clone (clone.S:100)
==3649251==  Address 0x10c080 is 0 bytes inside data symbol "m1"
==3649251== 
==3649251==  Lock at 0x10C0C0 was first observed
==3649251==    at 0x4850CCF: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x109284: worker (main-deadlock-global.c:13)
==3649251==    by 0x485396A: ??? (in /usr/libexec/valgrind/vgpreload_helgrind-amd64-linux.so)
==3649251==    by 0x48FEAC2: start_thread (pthread_create.c:442)
==3649251==    by 0x498FA03: clone (clone.S:100)
==3649251==  Address 0x10c0c0 is 0 bytes inside data symbol "m2"
==3649251== 
==3649251== 
==3649251== 
==3649251== Use --history-level=approx or =none to gain increased speed, at
==3649251== the cost of reduced accuracy of conflicting-access information
==3649251== For lists of detected and suppressed errors, rerun with: -s
==3649251== ERROR SUMMARY: 1 errors from 1 contexts (suppressed: 7 from 7)
```

按理来说，global mutex g 能保护 m1 和 m2 要么一起拿走，要么一起释放，不可能造成一个线程持有一个锁等待另一把锁 的死锁情况，为什么 Valgrind 工具依然报错? 原来 Valgrind 的设计理念检查的是“潜在死锁结构”，不是“是否真的会死锁”，有可能是会误报的。

## Question 6, 7
![alt text](image-1.png)

在 while 循环里多打一条输出，就可以发现问题：main thread 在等待 child thread 的时候，一直在自旋。

运行，居然有这么多 errors!

```
Possible data race during write ... by puts (ioputs.c:40)

==3660014== ERROR SUMMARY: 23 errors from 2 contexts (suppressed: 40 from 34)
```
 
在多个线程里同时调用 printf/puts，虽然 printf / puts 在多线程里是线程安全的，但在内存模型层面有 data race, 所以触发 Valgrind 的报错。

## Question 8，9

这个版本没有 data race. 

而且用 Pthread_cond_wait 来代替自旋。如果 signal 在 wait 之前发生，done = 1, 直接跳过 wait; signal 在 wait 之后发生, main 进入睡眠，worker signal 再把 main 唤醒。两种都是安全的。

```
==3671059== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 12 from 12)
```