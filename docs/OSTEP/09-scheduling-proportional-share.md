---
date: 2026-02-20
tags:
  - OSTEP
  - Scheduling
  - Concurrency
---

# 09. Scheduling: Proportional Share 

*写于 2026-02-20*

一个理想的公平调度应该长什么样？调度程序的最终目标，是确保每个工作获得一定比例的 CPU 时间，而不是优化周转时间和响应时间。

## **Lottery scheduling**

每个 runnable job 持有一定数量的 tickets，调度器在每次调度时随机抽取一张彩票，彩票所属的 job 获得 CPU。

Tickets Represent Your Share. 通过进程抽中的「彩票数」来决定具体的资源占用份额。

**Ticket Mechanisms**

-   Ticket Division: 一个 job 可以将自己的 tickets 分配给子任务。

-   Ticket Transfer: 当一个 job 因等待另一个 job 而阻塞时，它可以临时将自己的 tickets 转移给被等待者。

-   Ticket Inflation: 一个 job 可以临时增加自己的 tickets 数量，临时提高优先级。


Lottery Scheduling 的优点是足够简单，缺点是短时间内可能严重偏离比例。

## **Stride scheduling**

每个 job 被分配一个 stride，值与该 job 所分配的资源份额（tickets）成反比。调度器始终选择当前 pass 值最小的 job 运行，并在其运行后将其 pass 值增加对应的 stride。

Stride scheduling 是一种确定性的比例调度算法。比例是通过算术保证的，而不是概率保证的。

好处是：在任意前缀时间窗口内，都能保证 CPU 时间按票数比例分配（而Ticket Mechanisms 只有在运行时间足够长时才收敛到公平）

缺点：

1. Stride scheduling 需要为每个 runnable job 维护额外的调度状态（stride、pass），并在每次调度时从所有 runnable jobs 中选择 pass 最小者。

2. 新任务从中间插进来，就不是完美的公平了。pass 怎么设置？一定会破坏历史比例的连续性，可以设置成当前 pass 最小值。

## 总结

Lottery scheduling 和 Stride scheduling 原始设计是为了单处理器服务的。它们共同问题是：Lottery / Stride 调度器只在 runnable jobs 集合内分配 CPU，当一个 job 因 I/O 阻塞时，它会被移出 runnable 集合，不参与调度。此外，Lottery scheduling 如何为 jobs 分配初始彩票份额？这个问题还没有被解决。