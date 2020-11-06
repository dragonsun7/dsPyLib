# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-11-06 23:40:17'

# noinspection PyPackageRequirements
import progressbar  # https://www.jianshu.com/p/7e149c2cfdce

g_progress_bar = progressbar.ProgressBar()  # 进度条对象
g_show_progress_bar = True  # 是否显示进度条


# 设置是否显示进度条
def progress_init(show: bool = True):
    global g_show_progress_bar
    g_show_progress_bar = show


def progress_start(max_value: int):
    if (g_progress_bar is not None) and g_show_progress_bar:
        g_progress_bar.start(max_value)


def progress_update(value: int):
    if (g_progress_bar is not None) and g_show_progress_bar:
        g_progress_bar.update(value)


def progress_finish():
    if (g_progress_bar is not None) and g_show_progress_bar:
        g_progress_bar.finish()


if __name__ == '__main__':
    import time

    # progress_init(show=False)
    count = 100
    progress_start(max_value=count)
    for i in range(count):
        time.sleep(0.05)
        progress_update(value=i)
    progress_finish()
