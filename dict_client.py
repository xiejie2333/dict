"""
v 客户端，发送请求，接收结果展示
"""

from socket import *
import sys

# 服务器地址
ADDR = ("127.0.0.1", 8889)


# 客户端注册
def do_register(sockfd):
    while True:
        name = input("User:")
        passwd = input("Password:")

        if " " in name or " " in passwd:
            print("用户名密码不能包含空格")
            continue

        msg = "R %s %s" % (name, passwd)
        sockfd.send(msg.encode())  # 发送请求

        # 等结果
        result = sockfd.recv(128).decode()
        if result == 'OK':
            print("注册成功")
        else:
            print("注册失败")
        return


# 请求登录
def do_login(sockfd):
    name = input("User:")
    passwd = input("Password:")

    msg = "L %s %s" % (name, passwd)
    sockfd.send(msg.encode())  # 发送请求

    # 等结果
    result = sockfd.recv(128).decode()
    if result == 'OK':
        print("登录成功")
        login(sockfd, name)  # 进入二级界面
    else:
        print("登录失败")
    return


# 查询操作
def do_query(sockfd, name):
    while True:
        word = input("单词:")
        if word == '##':
            break
        msg = "Q %s %s" % (name, word)
        sockfd.send(msg.encode())  # 发送请求
        # 无论是否查询到都打印
        data = sockfd.recv(2048)
        print(data.decode())


# 历史记录
def do_history(sockfd, name):
    msg = "H " + name
    sockfd.send(msg.encode())  # 发送请求
    # 不确定循环次数时 死循环
    while True:
        # 每次接收一个历史记录
        data = sockfd.recv(1024).decode()
        if data == '##':
            break
        print(data)  # 接收什么内容直接打印


# 已经登录
def login(sockfd, name):
    while True:
        print("""
        ===============Query===============
         1.查单词     2.历史记录     3.注销
        ===================================
        """)
        cmd = input("请输入选项:")
        if cmd == '1':
            do_query(sockfd, name)
        elif cmd == "2":
            do_history(sockfd, name)
        elif cmd == "3":
            return
        else:
            print("请输入正确命令。")


# 连接服务端
def main():
    # 创建套接字
    try:
        sockfd = socket()
        sockfd.connect(ADDR)
    except:
        print("请检查你的网络后重试！")
        return

    # 进入一级界面
    while True:
        print("""
        ===========Welcome===========
         1.注册     2.登录     3.退出
        =============================
        """)
        cmd = input("请输入选项:")
        if cmd == '1':
            do_register(sockfd)
        elif cmd == "2":
            do_login(sockfd)
        elif cmd == "3":
            sockfd.send(b"E")
            sys.exit("谢谢使用")
        else:
            print("请输入正确命令。")


if __name__ == '__main__':
    main()  # 启动
