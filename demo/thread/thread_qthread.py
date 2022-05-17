# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 12:06:29'

"""
    线程：使用QThread(TODO)

    参考：
        https://zhuanlan.zhihu.com/p/364710810
"""

import time

from PySide2.QtCore import QObject, QThread


class Worker(QObject):

    def __init__(self):
        super(Worker, self).__init__()

    @staticmethod
    def run():
        print('a')
        time.sleep(0.5)


if __name__ == '__main__':
    thread = QThread()
    worker = Worker()
    worker.moveToThread(thread)
    thread.start()
