# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-20 14:30:37'

from typing import Generator, Sized


# 去掉列表中的重复项(http://www.chenxm.cc/article/541.html) (不能保持原顺序)
def remove_duplicate(the_list: list) -> list:
    temp_list = list(set([str(j) for j in the_list]))
    the_list = [eval(j) for j in temp_list]
    return the_list


def remove_duplicate_dict(dict_list: list) -> list:
    ret = [dict(t) for t in set([tuple(d.items()) for d in dict_list])]
    return ret


# 去掉列表重复项(保持原顺序)
# https://www.cnblogs.com/gcgc/p/11474369.html
# https://www.cnblogs.com/nyist-xsk/p/7473236.html
def remove_duplicate2(the_list: list) -> list:
    new_list = list(set(the_list))
    new_list.sort(key=the_list.index)
    return new_list


def equally(data: Sized, n: int) -> Generator:
    """
    将 data 均分为多份，每份中有n个元素
    如果 n <= 0，则触发异常
    如果 data 的长度为0，则返回无元素的生成器
    """
    assert n > 0, 'n必须为正整数'
    if len(data) == 0:
        return ()

    for i in range(0, len(data), n):
        yield data[i:i + n]


def equally2(data: Sized, n: int) -> Generator:
    """
    将 data 均分为 n 份，如果不能均分，则靠后的分组元素少
    如果 n <= 0，则触发异常
    如果 data 的长度为0， 则返回n个数组
    """
    assert n > 0, 'n必须为正整数'

    size = len(data)
    m = int(size / n)  # 每份多少个
    d = size % n  # 前面有几份，元素会多一个

    first = 0
    for i in range(n):
        last = first + m
        if i < d:
            last += 1
        yield data[first: last]
        first = last


if __name__ == '__main__':
    list1 = [1, 2, 1, 3, 2, 4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 9, 8, 0, 9]
    list2 = remove_duplicate2(list1)
    print(list2)
