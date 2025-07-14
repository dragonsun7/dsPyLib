# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-07-14 13:14:24'

import threading
import time
from typing import Optional

import rpyc
from rpyc.core.protocol import Connection
from rpyc.core.protocol import PingError

from dsPyLib.utils.logging import logger


class DSRPCClient:

    def __init__(self, 地址: str, 端口: int):
        """
        智能RPC客户端，自动管理连接状态
        :param 地址: 服务端主机地址
        :param 端口: 服务端端口
        """
        self.地址 = 地址
        self.端口 = 端口
        self.连接: Optional[Connection] = None

        self._最大重试次数 = 2
        self._心跳包间隔 = 30

        self._线程锁 = threading.Lock()  # 线程安全锁
        self._心跳循环标志位 = True
        self._启动心跳检测()

    # 支持直接调用方法：client.remote_method(args)
    def __getattr__(self, name):
        # 重定向方法调用到 调用远程方法（）
        def method_wrapper(*args, **kwargs):
            return self.调用远程方法(name, *args, **kwargs)

        return method_wrapper

    # 上下文管理器支持
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.关闭()

    def 关闭(self):
        """关闭连接并清理资源"""
        self._心跳循环标志位 = False
        if self.连接 and (not self.连接.closed):
            self.连接.close()
        self.连接 = None
        logger.info("连接已关闭")

    def 调用远程方法(self, 方法名称: str, *args, **kwargs):
        """
        调用远程方法
        :param 方法名称: 远程方法名称
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 远程方法执行结果
        """
        if not self._确保连接有效():
            raise ConnectionError("无法建立服务器连接")

        try:
            远程方法 = getattr(self.连接.root, 方法名称)  # 获取远程方法
            return 远程方法(*args, **kwargs)  # 执行远程调用
        except (EOFError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"调用期间连接断开: {e}")
            # 自动重连并重试一次
            if self._确保连接有效():
                远程方法 = getattr(self.连接.root, 方法名称)
                return 远程方法(*args, **kwargs)
            raise ConnectionError("重连失败，无法完成操作")
        except AttributeError:
            raise AttributeError(f"远程服务不存在方法: {方法名称}")

    def _连接服务器(self):
        """建立新连接（带重试机制）"""
        for 次数 in range(self._最大重试次数):
            try:
                logger.info(f"尝试连接 {self.地址}:{self.端口} (尝试 {次数 + 1}/{self._最大重试次数})")
                配置 = {
                    "allow_public_attrs": True,  # 允许公共属性访问(传递对象用)
                    "sync_request_timeout": 60,  # 设置超时时间
                }
                self.连接 = rpyc.connect(self.地址, self.端口, config=配置)
                logger.info("连接成功!")
                return True
            except (ConnectionRefusedError, TimeoutError) as e:
                等待时间 = 2 ** 次数  # 指数退避
                logger.error(f"连接失败: {e}. {等待时间}秒后重试...")
                time.sleep(等待时间)
        logger.error(f"无法连接服务器 {self.地址}:{self.端口}")
        return False

    def _确保连接有效(self):
        """确保连接有效（如果未连接或连接断开则自动重连）"""
        with self._线程锁:  # 确保线程安全
            if self.连接 is None:
                return self._连接服务器()

            try:
                # 快速检查连接是否存活
                if self.连接.closed:
                    logger.info("连接已断开，正在重新连接...")
                    return self._连接服务器()
                self.连接.ping()  # 如果不通会触发异常
                return True
            except (EOFError, BrokenPipeError, AttributeError, PingError):
                logger.error("连接异常，正在重新连接...")
                return self._连接服务器()

    def _启动心跳检测(self):
        """启动后台心跳检测线程"""

        def 心跳检测循环():
            while self._心跳循环标志位:
                # noinspection PyBroadException
                try:
                    if self.连接 and not self.连接.closed:
                        self.连接.ping(timeout=5)
                    time.sleep(self._心跳包间隔)
                except Exception:
                    pass  # 静默处理心跳异常，避免过多日志输出

        threading.Thread(target=心跳检测循环, daemon=True).start()


def demo():
    客户端 = DSRPCClient(地址='localhost', 端口=18812)
    返回值 = 客户端.hello()
    print(返回值)
    客户端.关闭()


def demo2():
    with DSRPCClient(地址='localhost', 端口=18812) as 客户端:
        返回值 = 客户端.hello()
        print(返回值)


if __name__ == '__main__':
    demo()
