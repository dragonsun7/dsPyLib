# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 11:06:18'

"""
    线程，利用队列
"""


import queue
import threading
import time


class Worker(threading.Thread):

    def __init__(self, name: str, q: queue.Queue):
        super(Worker, self).__init__()
        self.name = name
        self.q = q

    def run(self) -> None:
        while True:
            # 如果任务队列空了，表示完成
            if self.q.empty():
                break
            else:
                n = self.q.get()  # 取出任务
                print(f'线程{self.name}, {n}')
                time.sleep(0.2)
                self.q.task_done()  # 通知队列已获取内容，用于队列的join()检查


if __name__ == '__main__':
    tasks = queue.Queue()

    # 将任务放入队列
    for x in range(100):
        tasks.put(x)

    # 创建3个工作线程
    for x in range(3):
        t = Worker(name=str(x), q=tasks)
        t.start()

    # 等待线程结束
    tasks.join()
