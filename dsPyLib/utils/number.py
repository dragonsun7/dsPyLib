# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-20 14:35:38'

from math import nan, isnan


def is_odd(n: int) -> bool:
    """
    判断是否为奇数
    """
    return n % 2 == 0


def is_even(n: int) -> bool:
    """
    判断是否为偶数
    """
    return not is_odd(n)


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


def int_to_str(n: int) -> str:
    if n != 0:
        return str(n)
    else:
        return ''


def str_to_float(s: str) -> float:
    try:
        f = float(s)
    except ValueError:
        f = nan
    return f


def str_to_int(s: str) -> int:
    try:
        n = int(s)
    except ValueError:
        n = 0
    return n


def to_percent(f: float, digit: int = 2) -> str:
    """
    将浮点数转化为百分比字符串
        1. 乘以100
        2. 按照参数保留小数位数
        3. 尾部添加 '%'
        例如：0.223314, 2 => 22.33%
    @param f: 浮点数
    @param digit: 保留的小数位数(转换为百分比后的小数位数)
    @return: 百分比字符串
    """
    if isnan(f):
        return ''

    f *= 100
    fmt = f'%.{digit}f'
    return fmt % f + '%'
