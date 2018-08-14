# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'


import time
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
