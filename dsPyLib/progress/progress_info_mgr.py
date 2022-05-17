# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-07-28 18:58:32'

import datetime
import math

"""
    进度信息管理器
"""


class ProgressInfoManager(object):

    def __init__(self, on_changed):
        """
        @param on_changed: def (percent: float, whole: str, elapsed: str, remain: str)
        """
        self.on_changed = on_changed
        self.value = 0
        self.total = 0
        self.time_start = None
        self._init_flags()

    def start(self, total: int):
        self._init_flags()
        self.total = total
        self.time_start = datetime.datetime.now()

    def update(self, value: int):
        self.value = value
        self._do_changed()

    def finish(self):
        self.value = self.total
        self._do_changed()

    def _init_flags(self):
        self.value = 0
        self.total = 0
        self.time_start = None
        self._do_changed()

    def _do_changed(self):
        if self.on_changed is None:
            return

        # start
        if self.value == 0 or self.total == 0:
            self.on_changed(0, '--:--', '00:00', '--:--')
            return

        # finish
        if self.value == self.total:
            elapsed = datetime.datetime.now() - self.time_start
            s_elapsed = self._seconds_to_str(elapsed.seconds)
            self.on_changed(100, s_elapsed, s_elapsed, '00:00')
            return

        # update
        elapsed = datetime.datetime.now() - self.time_start
        elapsed_seconds = elapsed.seconds
        whole_seconds = math.ceil(elapsed_seconds / self.value * self.total)
        remain_seconds = math.ceil(elapsed_seconds / self.value * (self.total - self.value))
        s_whole = self._seconds_to_str(whole_seconds)
        s_elapsed = self._seconds_to_str(elapsed_seconds)
        s_remain = self._seconds_to_str(remain_seconds)
        percent = self.value / self.total * 100
        self.on_changed(percent, s_whole, s_elapsed, s_remain)

    @staticmethod
    def _seconds_to_str(seconds: int) -> str:
        minute = int(seconds / 60)
        second = seconds % 60
        s_minute = '%02d' % minute
        s_second = '%02d' % second
        ret = f'{s_minute}:{s_second}'
        return ret


if __name__ == '__main__':
    import time


    def handler_on_changed(percent: float, whole: str, elapsed: str, remain: str):
        print(f'percent = {int(percent)}, whole = {whole}, elapsed = {elapsed}, remain = {remain}')


    g_total = 10
    pm = ProgressInfoManager(on_changed=handler_on_changed)
    pm.start(g_total)
    for i in range(g_total):
        time.sleep(1)
        pm.update(i + 1)
    pm.finish()
