---
tags:
  - OSTEP
  - Process 
---

# 04. The Abstraction: The Process

OS 提供了一种 illusion，那就是有无数的 CPU 可以用。

## Virtualizing

Virtualization 的一个重要手段是 time sharing。

Policies 是操作系统做决策的算法。比如 Scheduling policy 是操作系统决定哪个进程先运行的算法。

## Process
 
Process 是操作系统为程序提供的抽象。

重点是深刻理解「程序就是状态机」。如何理解呢：

1. 寄存器的值，其中比较特殊的是 PC（程序当前在执行哪个指令）

2. 内存的内容：栈，堆，全局变量。（指令存在内存里。）

3. （多线程时）每个线程各自的 PC + 栈

以上整个集合，叫 program state. 在某一个瞬间，只要这些东西都确定了，程序接下来会做什么就是完全确定的。

## Process Creation

OS 在运行一个进程之前要做很多事情：

1. 加载程序的二进制可执行文件 .out 和静态数据到内存

    在最古老的操作系统里，OS 在创建进程之前，需要一次性把程序从 disk 加载到内存。

    现代操作系统 lazily 加载，在创建进程时只建立虚拟地址空间和页表映射，代码和数据在首次访问时通过 page fault 按需加载到物理内存。

    静态数据包括：

    `.text`：程序代码

    `.data`：已初始化的全局/静态变量

    `.bss`：未初始化的全局/静态变量（OS 会把它们初始化为 0）

    `.rodata`：只读数据，比如字符串常量


2. OS 为程序的运行时栈分配内存。

    OS 会为主线程分配运行时栈，通常在虚拟地址空间里预留一定大小（比如 8 MB）。对于多线程程序，OS 会为每个新线程分配自己的栈。

3. 可能为堆分配内存。

    OS 通常不会一次性分配整个堆，而是给进程一个初始的 heap 段空间（由 libc 管理）。
    当程序调用 `malloc()` 时，可能会触发 OS 系统调用（mmap）来扩展堆。

4. 初始化 I/O，打开标准输入，输出，错误

5. 跳转到函数入口 _start. 

    OS 并不知道你程序的 main() 在哪里。
    
    `_start` 是 C runtime（crt0）提供的入口：OS 让程序计数器（PC）指向 `_start`。
    
    `_start` 做一些初始化：

    - 设置 argc、argv、envp

    - 初始化全局构造函数（C++）

    - 调用 `main(argc, argv, envp)` 注意，main 是由 `_start` 调用的！

    - 调用 `exit()` 回到 OS

    OS 怎么知道 `_start` 在哪里呢？操作系统从 ELF 的入口点 `e_entry` 开始执行。链接器约定 `_start` 放在 `.text` 段的最前面。CPU 执行入口点地址对应的指令（一般就是 `_start`）。【后面应该还会学到的。】


## Process State

![alt text](image-6.png)

## Data Structures

OS 本身也是一个程序，它一个核心数据结构叫 PCB（Process Control Block，进程控制块），每个进程都有一个 PCB。这个维护的数据结构保证了当 CPU 从一个进程切换到另一个进程时，可以完整地保存和恢复执行状态。

一个简化的 PCB 的例子：

```c
typedef struct PCB {
    // 1️⃣ 进程标识
    int pid;               // 进程ID
    int ppid;              // 父进程ID
    char name[32];         // 进程名称

    // 2️⃣ 进程状态
    enum { NEW, READY, RUNNING, BLOCKED, TERMINATED } state;

    // 3️⃣ CPU 上下文（寄存器）
    unsigned long pc;      // 程序计数器（PC）
    unsigned long sp;      // 栈指针（SP）
    unsigned long regs[16]; // 通用寄存器，数量根据 CPU 架构不同

    // 4️⃣ 内存管理信息
    void *page_table;      // 指向页表或段表
    unsigned long heap_start; // 堆起始地址
    unsigned long heap_end;   // 堆结束地址
    unsigned long stack_base; // 栈底
    unsigned long stack_limit;// 栈顶

    // 5️⃣ 文件和 I/O
    int fd_table[16];      // 打开的文件描述符表

    // 6️⃣ 调度信息
    int priority;          // 优先级
    unsigned long cpu_time; // 已使用 CPU 时间
} PCB;
```