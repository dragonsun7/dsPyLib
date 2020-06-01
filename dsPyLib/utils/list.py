# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-20 14:30:37'


# 去掉列表中的重复项(http://www.chenxm.cc/article/541.html)
def remove_duplicate(the_list: list) -> list:
    temp_list = list(set([str(j) for j in the_list]))
    the_list = [eval(j) for j in temp_list]
    return the_list


def remove_duplicate_dict(dict_list: list) -> list:
    ret = [dict(t) for t in set([tuple(d.items()) for d in dict_list])]
    return ret
