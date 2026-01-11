---
tags:
  - OSTEP
  - Exceptional Control Flow
  - Concurrency
---

# 26. Concurrency and Threads

在单线程程序模型中，一个程序在任意时刻只有一个执行点，也只有一个 Program Counter，CPU 从该 PC 指向的位置取指并顺序执行。

而在多线程程序中，一个进程内部同时存在多个执行点。每个线程都有自己独立的 PC，操作系统通过调度机制在不同线程之间切换，使得来自不同线程的指令在时间上交错执行。

由于线程可能在任意时刻被抢占并在之后继续执行，操作系统必须能够记住每个线程的执行状态，以便之后恢复这个执行状态并继续执行。为此，操作系统为每个线程维护一个称为 Thread Control Block, TCB 的数据结构，用于记录线程的上下文信息。

一个典型的 TCB 包含以下内容：

```
TCB(Thread A):
    saved_PC = 0x400123
    saved_SP = 0x7fff...
    saved_regs = ...

TCB(Thread B):
    saved_PC = 0x4010ab
    saved_SP = 0x7ffe...
    saved_regs = ...
```

对于单核 CPU 的线程切换，任意时刻只能有一个线程实际运行。当操作系统从线程 A 切换到线程 B 时，会先将线程 A 当前的 CPU 状态（包括 PC、栈指针以及通用寄存器）保存到 TCB(Thread A) 中，然后将 TCB(Thread B) 中已经保存的状态恢复到 CPU 寄存器中。这样，线程 B 就可以从上一次被中断的位置继续执行。

需要注意的是，同一进程内线程之间的上下文切换不会切换地址空间。也就是说，线程切换时不需要更换页表，所有线程始终运行在同一个虚拟地址空间中。

在这个共享的地址空间内，线程之间堆共享，栈私有：线程共享同一地址空间，该地址空间中包含多个栈区，每个线程使用其中一个。如下图：

![alt text](image.png)

（顺便提一句，其实看右图能也能明白为何会 "stack overflow"。递归不能无限深，因为每个函数调用都会消耗线程栈空间，而线程栈只是进程虚拟地址空间中一段由操作系统限制大小的区域；当栈增长超过该限制时，会触发栈溢出异常。）
  
地址空间是谁分配的？是由操作系统在进程创建时“定义并管理”的。
  
为什么需要 threads? 

1. 提升效率。The task of transforming your standard single-threaded program into a program that does this sort of work on multiple CPUs is called parallelization, and using a thread per CPU to do this work is a natural and typical way to make programs run faster on modern hardware. 

2. 避免因缓慢的 I/O 操作而阻塞程序运行。
  
经典范例：创建两个线程 A 和 B，每个线程把全局变量 counter 加 1 一千万次，主线程等待它们结束，然后打印最终的 counter 值。

这个例子里，程序层面，两个线程 A、B 共享同一个地址空间，共享全局变量 counter。机器层面，counter++ 不是原子的，需要三个指令，分为 load, add, store 三个步骤。timer interrupt 可能发生在任意“指令边界”上，如果发生了 timer interrupt ，不管 CPU 正在执行哪条指令，硬件就向 CPU 发一个信号，切换到另一个 thread. （timer interrupt 是硬件中断，CPU 旁边有一个硬件定时器在独立地计数，时钟到点就触发。操作系统规定硬件定时器的触发频率，而 CPU 在中断发生时强制转入内核执行中断处理程序。）
  
错误发生的情况举例，程序执行了两个 add，但结果只加了一次：

```
Thread A: load counter → rA = 100
        (timer interrupt)
------------------------------
Thread B: load counter → rB = 100
Thread B: add 1 → rB = 101
Thread B: store → counter = 101
------------------------------
Thread A: add 1 → rA = 101
Thread A: store → counter = 101
```

（之前不是学到有[四种异常](../../csapp/8/#ecf) 吗，为什么说 interrupt 是异步的，是不是就是这个例子体现的？--也不是，异步异常是其发生时间不由当前正在执行的指令决定，而是由外部事件触发，比如定时器。上面这个例子中，异步不是错误的原因，数据竞争是错误的原因。即使异常是同步的，这个程序仍然会出错。）