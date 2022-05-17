# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 01:08:29'

import time

"""
    线程取消
        设置标志，在线程循环中进行判断
        可以利用Event类
"""

import threading


class TaskThread(threading.Thread):

    def __init__(self):
        super(TaskThread, self).__init__()
        self._cancel_event = threading.Event()

    def cancel(self):
        self._cancel_event.set()

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def run(self) -> None:
        while not self.is_cancelled():
            print('1')
            time.sleep(0.5)
        print('线程取消')


if __name__ == '__main__':
    t = TaskThread()
    t.start()
    time.sleep(3)
    t.cancel()
    t.join()
