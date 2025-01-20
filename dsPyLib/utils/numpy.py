# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-13 00:01:04'

import numpy


def 最大值索引(arr: numpy.ndarray) -> numpy.ndarray:
    if arr.size == 0:
        return numpy.array([])
    else:
        return numpy.flatnonzero(arr == numpy.max(arr))


def 最小值索引(arr: numpy.ndarray) -> numpy.ndarray:
    if arr.size == 0:
        return numpy.array([])
    else:
        return numpy.flatnonzero(arr == numpy.min(arr))


def 最大值最后索引(arr: numpy.ndarray) -> int:
    indexes = 最大值索引(arr)
    if indexes.size == 0:
        raise ValueError("数组为空，无法获取最大值索引")
    return int(indexes[-1])


def 最小值最后索引(arr: numpy.ndarray) -> int:
    indexes = 最小值索引(arr)
    if indexes.size == 0:
        raise ValueError("数组为空，无法获取最小值索引")
    return int(indexes[-1])


def demo():
    # 示例数据
    arr = numpy.array([1, 0, 0, 3, 2, 3, 4, 4, 4])
    print("数组:", arr)

    # 调用函数
    max_indices = 最大值索引(arr)
    print("所有最大值的索引:", max_indices)

    min_indices = 最小值索引(arr)
    print("所有最小值的索引:", min_indices)

    max_last = 最大值最后索引(arr)
    print("最后一个最大值的索引：", max_last)

    min_last = 最小值最后索引(arr)
    print("最后一个最小值的索引：", min_last)


if __name__ == '__main__':
    demo()
