# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 11:06:18'

"""
    线程，利用队列

    注意：这里是错误的做法！！！

    这是教科书级的经典竞态：两个 Worker 同时通过 empty() 检查（都看到还剩 1 个任务），
    其中一个 get() 取走最后一项后，另一个 get() 永久阻塞。由于 Worker 是非守护线程，进程将永远挂死。

    sys.setswitchinterval(interval) 用于设置 Python 解释器的线程切换间隔时间（单位为秒）。
    这个参数决定了 Python 的全局解释器锁（GIL）在多线程环境中多久释放一次，以便让其他线程有机会运行。
    默认值为0.005(5毫秒)，设置为0表示禁用切换
    sys.getswitchinterval() 查看当前设置值

    注意：
        不是真实并行：即使切换很快，Python 的 GIL 仍然限制同一时刻只有一个线程执行 Python 字节码
        OS 调度限制：实际切换还受操作系统调度器影响，设置过小可能被忽略
        设置过小可能导致：
            - CPU 使用率 100%
            - 程序变慢而非变快
            - 缓存失效增加

    在这里实测（放大竞态窗口：sys.setswitchinterval(1e-6) + 150 线程抢 5 个任务）
    将线程切换时间间隔设置为1微秒，这样就极大的提高了出现竞态的机会
    
    Queue的join和线程的join不一样
        Queue.join() 的语义：阻塞直到队列中所有任务都被 task_done() 处理完
        （内部数一个 unfinished_tasks 计数器：每 put() 一次 +1，每 task_done() 一次 -1，归零即返回）。
        
        关键：它完全不管线程死没死。 死锁的线程是阻塞在 get() 上的——它从没成功取到任务，也从没调用 task_done()，
        所以它压根不在计数器里，丝毫不影响 Queue.join() 返回。
        
        所以，有线程锁死，Queue().join()也会退出
        
        真正会等待线程退出的是threading.Thread.join()
        
    解决办法：将 
        n = self.q.get() 
        
        改成 
    
        try:
            n = self.q.get_nowait()  # 取出任务
            self.q.task_done()
        except queue.Empty:
            break
            
        get() 和 get_nowait() 的区别：
            get() 默认会阻塞等待
            get_nowait() 永远不等待，空队列时立即抛 queue.Empty 异常
"""

import queue
import sys
import threading
import time


class Worker(threading.Thread):

    def __init__(self, name: str, q: queue.Queue):
        super(Worker, self).__init__()
        self.name = name
        self.q = q

    def run(self) -> None:
        while True:
            if self.q.empty():
                # 如果任务队列空了，表示完成
                break
            else:
                n = self.q.get()  # 取出任务
                print(n)
                self.q.task_done()  # 通知队列已获取内容，用于队列的join()检查


if __name__ == '__main__':
    sys.setswitchinterval(1e-6)
    print(sys.getswitchinterval())

    incidents = 0

    for i in range(100):  # 测试100遍
        tasks = queue.Queue()

        # 将任务放入队列(创建5个任务)
        for x in range(5):
            tasks.put(x)

        # 创建150个工作线程
        workers = [Worker(name=str(x), q=tasks) for x in range(150)]
        for t in workers:
            t.daemon = True  # 为了即便线程锁死，程序也能正常退出
            t.start()

        # 等待队列任务完成
        tasks.join()

        # join() 返回瞬间最后一个 task_done() 的线程还活着（瞬态微秒级），直接判断 is_alive() 会产生假阳性，所以等待一个宽限期
        time.sleep(0.05)  # 宽限期(50毫秒)

        alive = sum(1 for t in workers if t.is_alive())
        if alive:
            incidents += 1

    print(f'结论: 150线程/5任务/100遍, 严格检测下 {incidents} 次真死锁')
