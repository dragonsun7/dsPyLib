# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-10-08 12:08:58'


# 将浮点数转换为保留指定小数位的字符串
def to_str(f: float, digit: int = 2) -> str:
    fmt = f'%.{digit}f'
    ret = fmt % f
    return ret


# 将浮点数保留指定小数位
def to_float(f: float, digit: int = 2) -> float:
    s = to_str(f, digit)
    ret = float(s)
    return ret
