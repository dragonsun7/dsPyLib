# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 00:36:01'

"""
    Thread示例：从Thread派生，Event类
        用于控制线程的执行
        Event类主要提供了三个方法：set(), clear(), wait()
        Event类内部定义了一个 _flag 标志，如果值为 False，则 wait() 会被阻塞， 如果值为 True，则 wait() 不再阻塞
        set() 将 _flag 设置为 True
        clear() 将 _flag 设置为 False
        is_set() 用于返回这个 _flag 的值
"""

import threading
import time

from dsPyLib.utils.style import color, FrontColor


# noinspection PyPep8Naming
class 信号灯线程(threading.Thread):

    def __init__(self, signal: threading.Event):
        super(信号灯线程, self).__init__()
        self.signal = signal

    def run(self) -> None:
        light = FrontColor.green  # 进入 run() 后会立即切换，也就是说初始是红灯

        # 每3秒切换一次红绿灯
        while True:
            if light == FrontColor.red:
                light = FrontColor.green
                tip = '绿灯'
                self.signal.set()  # 不再阻塞
            else:
                light = FrontColor.red
                tip = '红灯'
                self.signal.clear()  # 开始阻塞
            print(color(tip, light), flush=True)
            time.sleep(3)


# noinspection PyPep8Naming
class 车辆线程(threading.Thread):

    def __init__(self, signal: threading.Event):
        super(车辆线程, self).__init__()
        self.signal = signal

    def run(self) -> None:
        while True:
            self.signal.wait()
            print('通行', flush=True)
            time.sleep(1)


if __name__ == '__main__':
    event = threading.Event()

    信号灯 = 信号灯线程(signal=event)
    信号灯.start()

    车辆 = 车辆线程(signal=event)
    车辆.start()
