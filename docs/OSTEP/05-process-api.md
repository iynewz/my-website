---
tags:
  - OSTEP
  - Process 
---

# 05. Process API

What interfaces should the OS present for process creation and control?

## fork()

fork() 是 OS 提供的创建新进程的方法。

fork() 之后的返回值，Parent 进程获得的是子进程的 process id, 子进程获得的是 0.

## wait()

wait(NULL) 等待任意一个结束的子进程，返回值 rc_wait 是子进程的 PID, 这样就可以知道等到的是哪一个子进程。

如果想等一个特定子进程：

```c
pid_t rc = waitpid(child_pid, NULL, 0);
```

## exec()

Linux 上有六个 exec()：execl(), execv(), execle(), execve(), execlp(), execvp().

这六个里，只有 execve() 是 system call。 

execve() 发生在运行时，不是编译时（毕竟编译的时候也没进程）。

> What it does: given the name of an executable (e.g., wc), and some arguments (e.g., p3.c), it loads code (and static data) from that executable and overwrites its current code segment (and current static data) with it; the heap and stack and other parts of the memory space of the program are re-initialized. 

这段描述发生在 exec() 系统调用执行的那一刻。

在 exec() 成功时，内核停止当前进程的执行，丢弃当前进程的用户态地址空间（code segment, static data, heap, stack 都不要了），从磁盘读取 ELF 文件，加载新的程序，重新初始化 stack 和 heap. 设置 PC 为新程序入口 _start。

这也就是为什么 "after exec\n" 永远不会被打印，因为旧程序直接被抹掉了：

```c
int main() {
    printf("before exec\n");
    execve("/bin/ls", argv, envp);
    printf("after exec\n"); // execve 成功的话这里永远不会执行
}
```

正是因为 execve 会彻底替换当前进程的用户地址空间，所以它只能接受一个「已经编译、链接好的可执行文件」作为输入。

如果 exec 失败（原因比如没有执行权限，ELF 格式错误）那么旧地址空间不会被覆盖，原程序继续执行。

## 以 shell 为例，理解这样设计的用处

The shell is just a user program. Shell 不是内核的一部分，shell 也是一个用户态进程。以 shell 为例，因为有了 fork() 和 exec()，shell 可以fork() 创建子进程作为执行环境。在创建新进程之后，执行新程序之前，可以进行一些操作。

### 例子：redirect

```bash
ls > out.txt
```

shell 的逻辑其实就是 fork 和 exec：

```c
int fd = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);

pid_t pid = fork();

if (pid == 0) { // 子进程   
    // 1️⃣ 重定向 stdout
    dup2(fd, STDOUT_FILENO);
    close(fd);

    // 2️⃣ 执行新程序
    execvp("ls", argv);
    
    perror("exec"); // exec 失败才会到这里
    exit(1);
} else { // 父进程（shell）
    wait(NULL);
}
```

### 例子 2 - 管道

```bash
ls | wc -l
```

```c
int pipefd[2];
pipe(pipefd);  // pipefd[0] = 读端, pipefd[1] = 写端

// ---- 第一个子进程 ----
pid_t pid1 = fork();
if (pid1 == 0) {
    // 子进程 1: ls
    close(pipefd[0]);           // 关闭管道读端
    dup2(pipefd[1], STDOUT_FILENO); // stdout 重定向到管道写端
    close(pipefd[1]);           // dup2 后可以关写端原 fd
    execvp("ls", argv_ls);      // 执行 ls
    perror("exec ls");
    exit(1);
}

// ---- 第二个子进程 ----
pid_t pid2 = fork();
if (pid2 == 0) {
    // 子进程 2: wc -l
    close(pipefd[1]);           // 关闭管道写端
    dup2(pipefd[0], STDIN_FILENO);  // stdin 重定向到管道读端
    close(pipefd[0]);           // dup2 后关闭原 fd
    execvp("wc", argv_wc);      // 执行 wc -l
    perror("exec wc");
    exit(1);
}

// ---- 父进程 shell ----
close(pipefd[0]);
close(pipefd[1]);

waitpid(pid1, NULL, 0);  // 等 ls
waitpid(pid2, NULL, 0);  // 等 wc
```

哦莫，发现理解了这些，其实可以写一个支持有限功能的 shell 了？