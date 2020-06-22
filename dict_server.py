"""
c 逻辑控制， 基础结构搭建，接收请求，调用数据,数据整合提供给客户端
"""

from socket import *
from multiprocessing import Process
import signal, sys, time
from dict_db import *

# 全局变量
HOST = "0.0.0.0"
PORT = 8889
ADDR = (HOST, PORT)

# 实例化数据库对象
db = Database()


# 处理注册
def do_register(connfd, name, passwd):
    # 判断可否注册 --》 数据库处理 ->调用数据库方法解决问题
    # 返回True表示可以注册 False 表示注册不成功

    # 得到结果
    if db.register(name, passwd):
        connfd.send(b"OK")
    else:
        connfd.send(b"Fail")


# 登录处理
def do_login(connfd, name, passwd):
    if db.login(name, passwd):
        connfd.send(b"OK")
    else:
        connfd.send(b"Fail")


# 单词查询
def do_query(connfd, name, word):
    # 插入历史记录
    db.insert_history(name, word)

    # 查询单词
    mean = db.query(word)
    # 根据查询情况分情况处理  Yes 解释  No None
    if mean:
        data = "%s : %s" % (word, mean)
    else:
        data = "%s : Not Found" % word
    connfd.send(data.encode())


# 历史记录
def do_history(connfd, name):
    data = db.history(name)
    # data --> ((name,word,time),(),())
    for i in data:
        # i --> (name,word,time)
        msg = "%-10s   %-10s   %-s" % i
        connfd.send(msg.encode())  # 发送历史记录
        time.sleep(0.1)  # 防止沾包
    connfd.send(b'##')


# 处理客户端请求的进程
def handle(connfd):
    db.cursor()  # 每个子进程创建自己的游标
    # 接收某一个客户端的各种请求，分情况讨论处理
    while True:
        data = connfd.recv(1024).decode()
        tmp = data.split(' ')
        if not data or data == "E":
            # 客户端结束
            break
        elif tmp[0] == 'R':
            # tmp-->[R name passwd]
            do_register(connfd, tmp[1], tmp[2])
        elif tmp[0] == 'L':
            # tmp-->[L name passwd]
            do_login(connfd, tmp[1], tmp[2])
        elif tmp[0] == 'Q':
            # tmp-->[Q name word]
            do_query(connfd, tmp[1], tmp[2])
        elif tmp[0] == 'H':
            # tmp-->[H name]
            do_history(connfd, tmp[1])

    # 关闭子进程对应的资源
    connfd.close()
    db.cur.close()


# 网络并发模型
def main():
    # 创建tcp套接字
    sockfd = socket()
    sockfd.bind(ADDR)

    sockfd.listen(5)
    print("Listen the port %d" % PORT)

    # 处理僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    # 循环等待客户端连接
    while True:
        try:
            connfd, addr = sockfd.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            db.close()  # 关闭数据库连接
            sockfd.close()
            sys.exit("服务端退出")

        # 客户端连接则创建进程
        p = Process(target=handle, args=(connfd,))
        p.daemon = True
        p.start()


if __name__ == '__main__':
    main()  # 启动
