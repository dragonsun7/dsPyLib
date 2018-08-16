# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'


import time
import threading
import schedule
from enum import Enum
from functools import wraps


"""
    计算函数运行时间的修饰器
    使用方法：
        from dsPyLib.utils.decorator import *
        
        @elapsed
        def func():
"""


def elapsed(callback):
    """
    获取函数执行时间
    :param callback:
    :return:
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        # 记录下开始时间
        start = time.perf_counter()

        # 执行函数
        result = callback(*args, **kwargs)

        # 计算消耗时间
        elapse = time.perf_counter() - start

        # 输出信息
        func_file = callback.__code__.co_filename
        func_line = callback.__code__.co_firstlineno
        func_name = callback.__code__.co_name
        print(f'{func_file}, {func_line}, {func_name}() elapsed time: {elapse} seconds.')

        return result
    return wrapper


"""
    定时执行方法的修饰器
    使用方法：
        from dsPyLib.utils.decorator import *
        
        # interval 每隔多少秒执行(默认1); count 一共执行多少次(默认None，即不限次数)
        @timer(interval, count)     
        def func():
"""


def timer(interval=1, count=None):
    def _timer(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            def run():
                loop = 0
                while (not count) or (count and (loop < count)):
                    loop += 1
                    callback(*args, **kwargs)
                    if count and (loop >= count):
                        break
                    time.sleep(interval)

            thread = threading.Thread(target=run)
            thread.start()
        return wrapper
    return _timer


"""
    计划执行方法的修饰器
    使用方法：
        from dsPyLib.utils.decorator import *
        
        @scheduler(start_time, count, interval, unit)     
        def func():
"""


class CycleUnit(Enum):
    second = 'second'
    minute = 'minute'
    hour = 'hour'
    day = 'day'
    week = 'week'
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'
    sunday = 'sunday'


def scheduler(start_time=None, count=None, interval=1, unit=CycleUnit.day):
    """
    计划执行
    :param start_time: str, 开始时间，格式：%H:%M，例如：00:00(只有小时及其以上的单位才有效)
    :param count: int, 执行的次数，如果为None则不限次数
    :param interval: int, 周期间隔数量(monday到sunday，interval不生效)
    :param unit: CycleUnit, 周期单位 (例如：每3天执行一次，则 cycle_interval = 3, cycle_unit = CycleUnit.day)
    :return:
    """
    def _timer(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            cur_count = list()
            cur_count.append(0)

            def job(count_list):
                count_list[0] += 1
                callback(*args, **kwargs)

            def build_schedule():
                # 支持复数的周期单位
                plural_list = (CycleUnit.second, CycleUnit.minute, CycleUnit.hour, CycleUnit.day, CycleUnit.week)
                # 不支持at的周期单位
                no_at_list = (CycleUnit.second, CycleUnit.minute)

                is_plural = interval and (interval > 1) and (unit in plural_list)
                s_interval = str(interval) if is_plural else ''
                s_unit = unit.value + 's' if is_plural else unit.value
                s_at = '.at("%s")' % start_time if start_time and (unit not in no_at_list) else ''
                s_eval = 'schedule.every({interval}).{unit}{at}.do(job, cur_count)'.\
                    format(interval=s_interval, unit=s_unit, at=s_at)
                eval(s_eval, {'schedule': schedule, 'job': job, 'cur_count': cur_count})

            build_schedule()
            loop_count = count if count else 1
            while cur_count[0] < loop_count:
                schedule.run_pending()
                time.sleep(0.5)
        return wrapper
    return _timer
