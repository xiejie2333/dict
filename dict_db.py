"""
M 负责数据库处理
"""

import pymysql


# 数据库功能写在类中
class Database:
    def __init__(self):
        self.db = pymysql.connect(host="localhost",
                                  port=3306,
                                  user="root",
                                  password="123456",
                                  database="dict",
                                  charset="utf8")

    # 创建游标
    def cursor(self):
        self.cur = self.db.cursor()

    # 关闭数据库连接
    def close(self):
        self.db.close()

    # ===== 后面是功能性方法-》提供具体数据
    # 处理数据库层面的注册功能
    def register(self, name, passwd):
        sql = "select name from user where name=%s;"
        self.cur.execute(sql, [name])
        r = self.cur.fetchone()  # 能否查询到
        # 如果查询有这个那么则不能注册
        if r:
            return False
        # 插入操作
        sql = "insert into user (name,passwd) values (%s,%s);"
        try:
            self.cur.execute(sql, [name, passwd])
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            self.db.rollback()
            return False

    def login(self, name, passwd):
        # binary 让查询区分大小写
        sql = "select name from user \
              where binary name=%s and  binary passwd=%s;"
        self.cur.execute(sql, [name, passwd])
        r = self.cur.fetchone()  # 能否查询到
        # 如果查询有这个用户则成功
        if r:
            return True
        else:
            return False

    # 插入历史记录
    def insert_history(self, name, word):
        # id word time user_id
        sql = "select id from user where name=%s;"
        self.cur.execute(sql, [name])
        # fetchone() --> (id,)
        user_id = self.cur.fetchone()[0]

        sql = "insert into hist (word,user_id) values (%s,%s);"
        try:
            self.cur.execute(sql, [word, user_id])
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()

    # 查询单词
    def query(self, word):
        sql = "select mean from words where word=%s;"
        self.cur.execute(sql, [word])
        r = self.cur.fetchone()  # 查到 （mean,）  没有 None
        if r:
            return r[0]

    # 历史记录查询
    def history(self, name):
        # name word time
        sql = "select name,word,time from \
              user left join hist on user.id=hist.user_id \
              where name=%s order by time desc limit 10;"
        self.cur.execute(sql, [name])
        # （（name,word,time），（），（））
        return self.cur.fetchall()  # 提供所有查询结果
