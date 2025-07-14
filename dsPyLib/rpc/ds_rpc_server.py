# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-07-14 13:14:15'

import threading
from typing import Optional, Type, Union

import rpyc
from rpyc.utils.server import ThreadedServer

from dsPyLib.utils.logging import logger


class DSRPCServer(object):

    def __init__(self, 端口: int, 服务: Union[Type[rpyc.Service], rpyc.Service], 服务器描述: str = '', 显示服务器日志: bool = False):
        self.端口: int = 端口
        self.服务: Type[rpyc.Service] = 服务
        self.服务器描述: str = 服务器描述
        self.显示服务器日志: bool = 显示服务器日志

        self.运行中: bool = False
        self._服务器: Optional[ThreadedServer] = None
        self._服务器线程: Optional[threading.Thread] = None

    def 启动(self) -> Optional[Exception]:
        # 如果已经启动，则给出日志后退出
        if self.运行中:
            logger.warning('服务器已在运行中，无需重复启动')
            return ValueError('服务器已在运行中，无需重复启动')

        # 启动RPC服务器（非阻塞方式）
        try:
            协议配置 = {
                'allow_public_attrs': True,  # 允许公共属性访问(传递对象用)
                'allow_pickle': True,  # 建议关闭pickle，因为存在安全风险，pickle模块可能被用于执行任意代码(但是由于需要在客户端转换对象，所以这里打开)
                'allow_setattr': False,  # 禁止远程设置属性
                'allow_delattr': False,  # 禁止远程删除属性
                'sync_request_timeout': 300,  # 远程调用超时时间(秒)
            }
            服务器日志对象 = logger if self.显示服务器日志 else None
            self._服务器 = ThreadedServer(self.服务, port=self.端口, protocol_config=协议配置, logger=服务器日志对象)
            self._服务器线程 = threading.Thread(target=self._启动服务器, name=f'RPC-Server-{self.端口}', daemon=True)
            self._服务器线程.start()
            self.运行中 = True

            运行描述 = f'RPC Server started on port {self.端口}...'
            if self.服务器描述:
                运行描述 = self.服务器描述 + ' ' + 运行描述
            logger.info(运行描述)

            return None
        except PermissionError as e:
            logger.error('⚠️ 端口访问被拒绝：尝试选择更大的端口号(>1023)，或未被占用的端口号')
            return e
        except OSError as e:
            if 'Address already in use' in str(e):
                logger.error(f'⚠️ 端口 {self.端口} 已被占用')
            else:
                logger.error(f'⚠️ 操作系统错误: {str(e)}')
            return e
        except Exception as e:
            logger.error(f'⚠️ 其它错误: {str(e)}')
            return e

    def 停止(self) -> Optional[Exception]:
        if (not self.运行中) or (not self._服务器):
            logger.warning('服务器未运行，无需停止')
            return ValueError('服务器未运行，无需停止')

        try:
            self._服务器.close()
            self._服务器线程.join(timeout=5)  # 等待服务器线程结束
            logger.info(f'RPC服务器已停止')
            return None
        except Exception as e:
            logger.error(f'停止服务器时出错: {str(e)}')
            return e
        finally:
            self.运行中 = False
            self._服务器 = None
            self._服务器线程 = None

    def _启动服务器(self):
        # 实际运行服务器的内部方法
        try:
            self._服务器.start()
        except Exception as e:
            logger.error(f'RPC服务器意外停止: {str(e)}')
        finally:
            self.运行中 = False


def demo():
    import time
    from dsPyLib.rpc.ds_rpc_service import DSRPCService

    # 创建服务器实例
    服务器 = DSRPCServer(端口=18812, 服务=DSRPCService, 服务器描述='Hello服务', 显示服务器日志=True)

    # 启动服务器
    返回值 = 服务器.启动()
    if not isinstance(返回值, Exception):
        logger.info('服务器启动成功')
        while 服务器.运行中:
            time.sleep(1)
        服务器.停止()
    else:
        logger.info('服务器启动失败')


if __name__ == '__main__':
    demo()
