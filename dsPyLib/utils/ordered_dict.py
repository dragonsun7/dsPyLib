# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-06-16 02:54:57'

import math
from collections import OrderedDict


def equal_ordered_dict(d1: OrderedDict, d2: OrderedDict) -> bool:
    """
    判断两个OrderedDict的内容是否相等，主要针对nan进行了处理(因为两个nan比较会被认为不相等)
    比较包含三个方面：
        ①. 长度比较
        ②. 键名比较
        ③. 键值比较(针对nan进行处理)
    """
    # 首先长度比较
    if len(d1) != len(d2):
        return False

    for key1, val1 in d1.items():
        key2, val2 = d2.popitem(last=False)  # 从 d2 中按顺序取出键值对

        # 键名比较
        if key1 != key2:
            return False

        # 特别处理 nan 的情况
        if isinstance(val1, float) and isinstance(val2, float) and math.isnan(val1) and math.isnan(val2):
            continue

        # 值比较
        if val1 != val2:
            return False

    return True
