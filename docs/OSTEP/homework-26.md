---
comments: true
tags:
  - OSTEP
  - Exceptional Control Flow
---

# homework-26

## Readme
在开始作业之前，一定要读官方仓库中的说明：https://github.com/remzi-arpacidusseau/ostep-homework/tree/master/threads-intro

`x86.py` 是一个教学用的 x86-like CPU 模拟器，用于直观展示多线程程序在不同调度下的执行过程。为简化模型，`.text` 段从地址 1000 开始。

README 演示了 `x86.py` 的基本用法及参数选项，它用一个小例子展示了并发程序中的核心问题：当线程在由多条非原子指令构成的操作序列中被抢占并发生交错执行时，可能产生典型的并发错误（race condition）。

运行 README 里提到的示例程序：

`./x86.py -p looping-race-nolock.s -t 2 -a bx=1 -M 2000 -c`

该命令创建两个线程，每个线程的寄存器 `bx = 1`，即每个线程各自执行一次 `counter++`。命令要求列出内存地址 2000 处的值。

```
 2000          Thread 0                Thread 1         
    0   
    0   1000 mov 2000, %ax
    0   1001 add $1, %ax
    1   1002 mov %ax, 2000
    1   1003 sub  $1, %bx
    1   1004 test $0, %bx
    1   1005 jgt .top
    1   1006 halt
    1   ----- Halt;Switch -----  ----- Halt;Switch -----  
    1                            1000 mov 2000, %ax
    1                            1001 add $1, %ax
    2                            1002 mov %ax, 2000
    2                            1003 sub  $1, %bx
    2                            1004 test $0, %bx
    2                            1005 jgt .top
    2                            1006 halt
```

这个结果只是比较幸运，调度点（`Halt;Switch`）发生在 Thread 0 完全结束之后，因此两个线程对共享变量的更新没有发生交错，最终 `m[2000]` 的结果为 2。

这并不意味着程序是线程安全的。如如果显式指定更频繁的中断，如指定：`-i 2` 每两条指令中断一次：`./x86.py -p looping-race-nolock.s -t 2 -a bx=1 -M 2000 -i 2 -c`

```
 2000          Thread 0                Thread 1         
    0   
    0   1000 mov 2000, %ax
    0   1001 add $1, %ax
    0   ------ Interrupt ------  ------ Interrupt ------  
    0                            1000 mov 2000, %ax
    0                            1001 add $1, %ax
    0   ------ Interrupt ------  ------ Interrupt ------  
    1   1002 mov %ax, 2000
    1   1003 sub  $1, %bx
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1002 mov %ax, 2000
    1                            1003 sub  $1, %bx
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1004 test $0, %bx
    1   1005 jgt .top
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1004 test $0, %bx
    1                            1005 jgt .top
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1006 halt
    1   ----- Halt;Switch -----  ----- Halt;Switch -----  
    1                            1006 halt
```

可以看到，`m[2000]` 的结果为 1. 这个例子说明了，并发错误并非每次执行都会显现，而是与调度时机（本实验里的 `-i` interrupt frequency）有关。

接下来可以做作业了，但如果只是贴跑出来的答案，那没有什么分享价值，因为大家按要求都能跑出一样的结果，所以我写了一点点分析。

(这个作业整体不难，如果有时间可以读一下老师实现的 `x86.py` 应该会有很多收获。)

## Question 1

运行 `./x86.py -t 1 -p loop.s -i 100 -R dx -c`

`-i 100` 表示每 100 条指令中断一次，`loop.s` 一共才 4 条指令，不会触发 interrupt.

```
   dx          Thread 0         
    0   
   -1   1000 sub  $1,%dx
   -1   1001 test $0,%dx
   -1   1002 jgte .top
   -1   1003 halt
```


## Question 2

`./x86.py -p loop.s -t 2 -i 100 -a dx=3,dx=3 -R dx -c`

引入 2 个线程，每个线程有自己独立的寄存器，所以 command 里 `dx=3,dx=3` 需要设置 2 个寄存器。

没有发生 race condition，因为 `dx` 初始值很小 (`dx = 3`)，10 条指令就能结束。而编译选项设置了每 100 条指令中断一次。一个线程完整执行，没发生指令之间的中断。

## Question 3
`./x86.py -p loop.s -t 2 -i 3 -r -R dx -a  dx=3,dx=3`

`-i 3` 设置了每 3 条指令中断一次，`-r` 让中断随机位置发生。初次理解时我疑惑这两个不是矛盾的吗？再仔细读一下 README, 发现 `-i` 和 `-r` 两个 options 连用是触发随机中断 `[1, 3]` 条指令。
`-s` 设置随机数种子。

```
   dx          Thread 0                Thread 1         
    3   
    2   1000 sub  $1,%dx
    3   ------ Interrupt ------  ------ Interrupt ------  
    2                            1000 sub  $1,%dx
    2                            1001 test $0,%dx
    2                            1002 jgte .top
    2   ------ Interrupt ------  ------ Interrupt ------  
    2   1001 test $0,%dx
    2   1002 jgte .top
    1   1000 sub  $1,%dx
    2   ------ Interrupt ------  ------ Interrupt ------  
    1                            1000 sub  $1,%dx
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1001 test $0,%dx
    1   1002 jgte .top
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1001 test $0,%dx
    1                            1002 jgte .top
    1   ------ Interrupt ------  ------ Interrupt ------  
    0   1000 sub  $1,%dx
    0   1001 test $0,%dx
    1   ------ Interrupt ------  ------ Interrupt ------  
    0                            1000 sub  $1,%dx
    0                            1001 test $0,%dx
    0                            1002 jgte .top
    0   ------ Interrupt ------  ------ Interrupt ------  
    0   1002 jgte .top
    0   ------ Interrupt ------  ------ Interrupt ------  
   -1                            1000 sub  $1,%dx
    0   ------ Interrupt ------  ------ Interrupt ------  
   -1   1000 sub  $1,%dx
   -1   1001 test $0,%dx
   -1   1002 jgte .top
   -1   ------ Interrupt ------  ------ Interrupt ------  
   -1                            1001 test $0,%dx
   -1                            1002 jgte .top
   -1   ------ Interrupt ------  ------ Interrupt ------  
   -1   1003 halt
   -1   ----- Halt;Switch -----  ----- Halt;Switch -----  
   -1                            1003 halt
```

虽然发生了 interleaving, 但 `loop.s` 没有访问共享内存，而是每个线程对自己的寄存器操作，所以不会有 race condition. `dx` 结果不变。

## Question 4

`./x86.py -p looping-race-nolock.s -t 1 -M  2000`

内存地址 2000 处的值从零自增为 1

## Question 5

`./x86.py -p  looping-race-nolock.s -t 2 -a bx=3 -M 2000`

这里感觉 command 写得不够标准，应该 `bx=3, bx=3` 设置 2 个寄存器？

因为 `bx` 初始化为 3，每次循环判断 %bx 减去 1 后是否还 > 0，如果是就跳回 .top，所以对于每个线程而言，.top 执行 3 次。单个线程把 value 增加 3，两个线程把 value 增加到 6。

## Question 6

`./x86.py -p  looping-race-nolock.s -t 2 -M 2000 -i 4 -r -s 0`

`-s 0` 或 `-s 1`，或 `-s 2` 会调整中断发生的位置。只要中断没有发生在临界区，内存地址 2000 处的值就是正确的 2。`-s 0` 和 `-s 2` 的运行结果是 2，但 `-s 1` 会让中断发生在临界区，结果是 1.

这三行指令是临界区，如果被打破了，就可能发生 race condition:

```
mov 2000, %ax  # get 'value' at address 2000
add $1, %ax    # increment it
mov %ax, 2000  # store it back
```

## Question 7

`./x86.py -p  looping-race-nolock.s -a bx=1 -t 2 -M 2000 -i 1`

`-i 1` 每条指令中断一次，肯定会进入临界区；-i 2 也是进入临界区，共享变量值为 1.

`-i 3` 恰好绕开临界区，共享变量值也恰好正确。

## Question 8

`-i` 的参数只有是 3 才倍数，才能恰好绕开临界区，共享变量值也恰好正确。其他值结果都不对。

## Question 9

`./x86.py -p  wait-for-me.s -a ax=1,ax=0 -R ax -M 2000 -c`

Thread 0 初始 `ax = 1`，因此进入 .signaller，将共享内存地址 2000 的值设置为 1 并随后结束执行。

在某个调度点，CPU 切换到 Thread 1。Thread 1 初始 `ax = 0`，进入 .waiter，反复读取共享变量并测试其值是否为 1。由于此时共享变量已经被 Thread 0 更新为 1，Thread 1 很快跳出 busy-wait 循环并正常结束。

这个问题实现了一个危险的 busy waiting：线程通过不断轮询共享内存来等待条件成立，尽管在该执行顺序下两个线程最终都能正确结束，但这种同步方式是危险的。这就是下一道题想说明的：

## Question 10

`./x86.py -p wait-for-me.s -a  ax=0,ax=1 -R ax -M 2000 -c`

Thread 0 初始 `ax = 0`，首先进入 .waiter，并在共享变量尚未被设置为 1 的情况下进行 busy waiting，无法退出循环。直到发生一次调度切换，Thread 1 获得 CPU 执行机会，进入 .signaller，将共享内存地址 2000 的值设置为 1。随后再次切换回 Thread 0 时，waiter 线程才能观察到条件成立并跳出循环，最终结束执行。

因为 signaller 迟迟没有写入 1，waiter 线程将持续占用 CPU 空转，造成资源浪费。