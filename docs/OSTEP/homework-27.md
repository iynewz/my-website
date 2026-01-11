---
comments: true
tags:
  - OSTEP
  - Concurrency
---

# homework-27

Valgrind 是一个运行时工具。它在自己的执行引擎下运行程序，并允许不同的工具检查程序的内存使用、线程行为以及性能。

Valgrind 对软件正确性工具的发展产生了巨大影响，像 AddressSanitizer（ASan） 这样的工具很可能就是受到了 Valgrind 的启发。

直到今天，Valgrind 仍然被广泛用于内存调试和性能分析，尤其是在 C/C++ 程序中。

Helgrind 是 Valgrind 中的一个工具，用于检测使用 POSIX pthreads 线程原语 的 C、C++ 和 Fortran 程序中的同步错误。  

## Question 1

```
make
gcc -g -pthread main-race.c -o main-race
```

POSIX 线程是 OS / libc 提供的能力，需要用 `-pthread` 明确让编译器启用并对接这套线程模型。

先直接运行看看行为：

```
./main-race
```

没有输出。我们来看下源代码：

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

程序一开始只有 main() 一个线程，`Pthread_create()` 创建了一个新线程 p，p 开始执行 `worker()`。此时，两个线程并发执行。这两个线程都对共享变量执行了增加操作，而且没有锁，可能发生 data race. 

main() 执行到 `Pthread_join()`，阻塞当前调用者线程 main()，直到线程 p 结束。但，这个时候阻塞也没有意义，之前已经两个线程并发操作共享变量了。

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

mutex 保证同一时间内，只有一个线程可以进入锁保护的临界区。锁只约束使用它的线程。worker 不受 mutex 的约束，data race 完全有可能发生！

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

