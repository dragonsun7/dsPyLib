# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-07-14 14:53:24'

import rpyc


@rpyc.service  # 要使用 @rpyc.exposed 装饰器，就必须加这个装饰器
class DSRPCService(rpyc.Service):

    def __init__(self):
        self.连接池 = []

    def on_connect(self, conn):  # 当连接时触发
        self.连接池.append(conn)

    def on_disconnect(self, conn):  # 当断开连接时触发
        # 主动移除断开客户端的引用，避免残留连接导致 EOFError 或资源泄漏
        if conn in self.连接池:
            self.连接池.remove(conn)

    # 一个默认的，用于测试的方法
    @rpyc.exposed
    def hello(self) -> str:
        return 'Hello'
