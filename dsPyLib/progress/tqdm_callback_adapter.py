"""
    需求：
        有一个现成的第三方对象（或者系统），它在运行过程中只会向外抛出 开始、更新、结束 这三种事件（也就是回调）
        然后想把这些事件“桥接”到 tqdm 的进度条上。

    Processing...: 100%|██████████| 100/100 [00:10<00:00,  9.70bar/s, count=100, count1=100]
        │                                                       │       │          │
      desc                                                     unit     └─  extra ─┘
"""

import time
from typing import Optional, Dict

from tqdm import tqdm


class TqdmCallbackAdapter:

    def __init__(self):
        self.progress_bar: Optional[tqdm] = None

    def start(self, total: int, desc: str = 'Processing...', unit: str = 'bar'):
        self.progress_bar = tqdm(total=total, desc=desc, unit=unit)

    def update(self, current: int, extra: Optional[Dict] = None):
        if self.progress_bar:
            step = current - self.progress_bar.n
            if step > 0:
                self.progress_bar.update(step)
            if extra:
                self.progress_bar.set_postfix(extra)

    def finish(self):
        if self.progress_bar:
            self.progress_bar.n = self.progress_bar.total
            self.progress_bar.close()
            self.progress_bar = None


def demo():
    class Biz:
        def __init__(self):
            self.start_callback = None
            self.update_callback = None
            self.finish_callback = None

        def foo(self):
            total = 100
            if self.start_callback:
                self.start_callback(total=total)
            try:
                for i in range(total):
                    if self.update_callback:
                        self.update_callback(current=i, extra={'count': i + 1, 'count1': i + 1})
                    time.sleep(0.1)
            finally:
                if self.finish_callback:
                    self.finish_callback()

    adapter = TqdmCallbackAdapter()
    biz = Biz()
    biz.start_callback = adapter.start
    biz.update_callback = adapter.update
    biz.finish_callback = adapter.finish
    biz.foo()


if __name__ == '__main__':
    demo()
