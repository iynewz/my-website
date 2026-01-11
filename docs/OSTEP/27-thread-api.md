---
tags:
  - OSTEP
  - Thread
  - Concurrency
---

# 27. Thread API

这一章解决的问题是，如何创建和控制 threads.

## pthread_create

```c
int pthread_create(pthread_t *thread,
                   const pthread_attr_t *attr,
                   void *(*start_routine)(void*),
                   void *arg);
```

第一个参数用于存放新创建线程的标识符（ID），后续可以用这个 ID 来操作线程（如 join、cancel 等）

第二个参数可设置的属性包括栈大小、调度策略和优先级，一般默认 NULL。

第三个参数是线程函数 start_routine 的指针，线程启动后，控制流跳转到这个函数。

第四个参数是传递给线程函数的参数，就是 start_routine 函数接收的那个 `void*` 参数，可以传递任意类型的数据（通过指针转换）。

深入理解 `void*`: 物理层面，第四个参数传递一个机器字长的位模式，比如 64 位系统，第四个参数就是传一个 64 位数。使用 `void*` 使得我们可以传入任意类型的参数（或返回任意类型的参数）。

## pthread_join()

```c
int pthread_join(pthread_t thread, void **retval);
```

pthread_join() 阻塞调用线程，直到指定的线程 thread 终止执行。

第一个参数：被等待线程

第二个参数：用于接收被等待线程的返回值。

如果调用者不需要线程的返回值：`pthread_join(tid, NULL)`;

为什么第二个参数是 pointer to pointer 类型？

因为函数参数是实参的拷贝，只有通过传递地址，才能在被调用函数中修改调用者可见的状态。线程返回的是 `void *`, 所以必须传入该指针的地址（即一个指向 `void *` 的指针），才能写回结果。

注意，线程结束时，其栈帧被销毁，千万不能返回指向栈上对象的指针。

依次地 pthread_create 一次、pthread_join 一次，在语义上其实等价于一次 procedure call. 所以一般不会这样用。

多线程模型并不是一定要 join 的，比如：在 server-style 线程模型里，服务器程序通常先创建一定数量的 worker 线程，主线程持续地接收请求（ accept()），并将请求分发给 worker 线程处理。worker 线程通常是长期运行的，因此主线程不一定需要调用 pthread_join()。

## 锁

初始化有 2 种方法：

- 静态初始化  
 
      ```
      pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
      ```
  
- 动态初始化
    
     ```c
     pthread_mutex_t lock;
     int rc = pthread_mutex_init(&lock, NULL);
     assert(rc == 0);   // 始终检查返回值
     ```

     第一个参数是互斥锁对象本身的地址，因为 pthread_mutex_init() 需要修改 mutex 对象的内部状态。
    
     第二个参数指定互斥锁的属性，默认 NULL。

## Condition Variables

### 为什么需要条件变量？

锁只能保证互斥访问临界区，即同一时刻只有一个线程能够操作共享数据，但不能解决「等待条件成立」。

在并发场景里，thread 通常需要「当条件不满足时阻塞等待；当条件成立时被及时唤醒并继续执行」。

如果没有条件变量，只能采用以下两种方式：

1. 必须忙等
    
    假设当前线程是消费者，另一个线程（生产者）会在未来某个时间把数据放进 queue。消费者的操作依赖 “queue 非空”，最糟糕的代码是：
     
    ```c
    while (queue_empty()) {
        // do nothing
    }
    ```
    忙等会导致线程持续占用 CPU 反复检查条件，造成严重的 CPU 浪费。

2. sleep 轮询等待
      
    ```c
    lock(mutex);
    while (queue_empty()) {
        unlock(mutex); // 在进入休眠前释放锁
        sleep(1); // 当前（消费者）线程休眠1秒
        lock(mutex); // 醒来后，再次尝试获取锁，以便能安全地检查队列状态。获取到锁后，循环回到第 2 步 while (queue_empty()) 重新检查队列
    }
    consume();
    unlock(mutex);
    ```
    
    调用 `sleep(1)` 会使当前线程阻塞，并从调度器的运行队列中移除。内核记录其唤醒时间点，在随后的定时器中断处理中，当系统时间达到或超过该时间点时，将该线程重新标记为可运行。

    `sleep(1)` 之后，程序会从 sleep 调用之后的位置自动继续执行，即执行 `lock(mutex)`;
    
    这段代码里只 `consume()` 一次就结束了。在实际应用中，这通常是不完整的，消费者线程应该是一个无限循环，持续不断地消费（外面再包一层 while true）
    
    `sleep(1)` 是忙等的改进版，但依然存在缺点，如即使生产者 0.1 秒后放入了数据，消费者也最多要等 1 秒才能醒来处理，响应不及时。而且，虽然比纯粹的 `while (queue_empty())` 空转节省了CPU，但依然存在不必要的周期性唤醒和锁操作。
    
    在并发编程中，处理这种“等待某个条件成立”的场景，标准且高效的做法是使用“条件变量”。

### POSIX 库提供的 condition variable

```c
int pthread_cond_wait(pthread_cond_t *cond,
                      pthread_mutex_t *mutex);

int pthread_cond_signal(pthread_cond_t *cond);
```

pthread_cond_wait() 做了三件事：

1. 释放 mutex（这就是为什么第二个参数是一个 mutex）
   
2. 把线程放入 cond 的等待队列，并进入睡眠 puts the calling thread to sleep, releases the lock。
   
3. （被唤醒之后），重新获取 mutex。pthread_cond_wait 返回之前，线程一定已经重新拿到了 mutex

     > However, before returning after being woken, the `pthread_cond_wait()` re-acquires the lock, thus ensuring that any time the waiting thread is running between the lock acquire at the beginning of the wait sequence, and the lock release at the end, it holds the lock.

### 如何协作？

以下这段代码是一个完整的 consumer - producer 示例：

signal 只需要一个参数 cond：告诉等待在这个 condition variable 上的线程，条件可能发生变化了。

```c
#include <pthread.h>
#include <stdio.h>

pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
int ready = 0;

void* consumer(void* arg) {
    pthread_mutex_lock(&lock);
    while (ready == 0)
        pthread_cond_wait(&cond, &lock);  // 阻塞等待
    printf("Consumer: ready = %d\n", ready);
    pthread_mutex_unlock(&lock);
    return NULL;
}

void* producer(void* arg) {
    pthread_mutex_lock(&lock);
    ready = 1;                           // 修改条件
    pthread_cond_signal(&cond);          // 唤醒等待线程
    pthread_mutex_unlock(&lock);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, consumer, NULL);
    pthread_create(&t2, NULL, producer, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}
```