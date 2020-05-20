# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-20 14:35:38'


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
