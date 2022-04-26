# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-20 14:35:38'

from math import nan, isnan


def get_decimal_digit(f: float) -> int:
    """
    获取一个数的小数点后的位数
    例如：5 ->0; 5.001 -> 3
    :param f:
    :return:
    """
    if type(f) == int:
        return 0
    else:
        num = 1
        while f * 10 ** num != int(f * 10 ** num):
            num += 1
        return num


def float_to_str(f: float, digit: int = 2, is_ratio: bool = False) -> str:
    """
    将浮点数转成字符串
    :param f: 浮点数
    :param digit: 保留的小数位数
    :param is_ratio: 是否为百分比(如果是，则会乘以100并加上百分号)
    :return:
    """
    if isnan(f):
        return ''
    if is_ratio:
        f = f * 100
    fmt = f'%.{digit}f'
    s = fmt % f
    if is_ratio:
        s = s + '%'
    return s


def str_to_float(s: str) -> float:
    try:
        f = float(s)
    except ValueError:
        f = nan
    return f
