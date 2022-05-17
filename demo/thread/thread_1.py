# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-16 23:59:08'

"""
    Thread示例：直接使用Thread类
"""

import threading
import time


def thread_func(msg: str):
    for n in range(10):
        print(f'{n}, {msg}, {threading.current_thread()}\n')
        time.sleep(1)


if __name__ == '__main__':
    # 在 start() 之前设置 线程.daemon = True，则为守护线程，优先级别最低
    # 如果所有的非守护线程(主线程以及子线程）都结束了，守护线程自动就会终止
    # 所以守护线程一般都为死循环，可以不用 join()

    tasks = []

    t1 = threading.Thread(target=thread_func, args=['线程1'])
    t1.start()
    tasks.append(t1)

    t2 = threading.Thread(target=thread_func, args=['线程2'])
    t2.start()
    tasks.append(t2)

    for t in tasks:
        t.join()
