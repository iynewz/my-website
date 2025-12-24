---
tags:
  - CSAPP
  - Network
---

# Tiny server

## TODO
* [x] 最小的 webserver: nc-l
* [ ] 一步步进化为生产可以用的就难了。难的是并发、动态内容、c-10k、c-100k
  

## 最小的 Server

即便是最简单的服务器，也完全涵盖了 TCP 的核心机制——socket → bind → listen → accept → read/write

我们先实现一个极简服务器，代码如下：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main()
{

    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(8080);

    bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr));
    listen(listen_fd, 5);
    int conn_fd = accept(listen_fd, NULL, NULL);

    char buf[1024];
    int n = read(conn_fd, buf, sizeof(buf) - 1);
    buf[n] = '\0';
    printf("Received: %s\n", buf);

    close(conn_fd);
    close(listen_fd);
    return 0;
}
```

这个服务器的核心流程是：

1. socket() 
    创建一个 TCP Socket 对象，返回文件描述符 listen_fd，此时这个 socket 只是一个内核分配的、尚未与任何本地地址或端口关联的网络端点。

2. bind()
    将 Socket 绑定到本地地址和端口（本例是 0.0.0.0:8080），操作系统内核维护端口与 Socket 的映射。

3. listen()
    将 Socket 设置为被动监听模式。

4. accept()
    从完成三次握手的连接队列中取出一个连接，返回新的文件描述符 conn_fd，用于与客户端通信。listen_fd 仍然保持监听状态，可接收更多客户端。

5. read() / write()
    与客户端进行数据传输。

运行这个程序，此时服务器会阻塞在 accept() 等待客户端连接。在另一终端用 `lsof -i :8080` 验证端口是否在监听：

```
COMMAND  PID  USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
test    7199 wenyi    3u  IPv4 0xec0ceef53bfdfffd      0t0  TCP *:http-alt (LISTEN)
```

可以看到最后的 “LISTEN”，表示内核此时维护监听队列。

接着，使用 netcat 连接服务器：

```
nc 127.0.0.1 8080
```

此时尚未输入任何内容，再次查看 `lsof -i :8080`：

```
COMMAND   PID  USER   FD gi  TYPE   DEVICE SIZE/OFF NODE NAME
test    24637 wenyi    3u  IPv4  TCP *:http-alt (LISTEN)
test    24637 wenyi    4u  IPv4  TCP localhost:http-alt->localhost:56232 (ESTABLISHED)
nc      24786 wenyi    3u  IPv4  TCP localhost:56232->localhost:http-alt (ESTABLISHED)
```

* FD=3：服务器监听 Socket (listen_fd)
* FD=4：服务器与 nc 客户端建立的连接 (conn_fd)
* nc FD=3：客户端 Socket
* 两个 ESTABLISHED 表示 TCP 三次握手已完成，内核完成了连接的状态转换

注意，accept() 会生成一个新的 fd（也就是本例的 FD=4），专门处理客户端连接，原始 listen_fd 继续监听端口。