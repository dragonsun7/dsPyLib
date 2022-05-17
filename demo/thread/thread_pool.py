# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 11:37:33'

"""
    线程：线程池
    
        线程池可以提高性能，防止启动大量线程而导致系统变慢，可以更简单的创建线程，适用于突发大量线程，而线程存在时间短的场景。
        
        线程池由concurrent.futures下的ThreadPoolExecutor提供
        submit(fn, *args，**kwargs)将函数fn提交给线程池，后面是参数
        map(fn，*iterables,timeout=None，chunksize=1)启动多线程
        让函数fn分别使用后面的可迭代参数shutdown(wait=True)关闭线程池

        使用submit()函数提交后会返回一个Future对象
        cancel()可以取消该线程，如果线程正在运行，不可取消，返回False，否则取消线程，并返回True
        cancelled()返回线程是否被取消
        running()返回线程是否正在运行
        done()返回线程是否完成，包括取消和正常完成
        result(timeout=None)获取该线程的返回结果，会阻塞线程
        timeout是阻塞时间add_done_callback(fn)线程结束后执行fn函数
"""

import time
from concurrent.futures import ThreadPoolExecutor


def run(n: int):
    print(f'线程{n}启动')
    time.sleep(1)


if __name__ == '__main__':
    pool = ThreadPoolExecutor(max_workers=2)  # 线程池最大容量设置为2

    # 启动三个线程(前两个结束后才轮到第三个)
    t1 = pool.submit(run, 1)
    t2 = pool.submit(run, 2)
    t3 = pool.submit(run, 3)

    # 查看
    print(t1.done())
    print(t2.done())
    print(t3.done())
