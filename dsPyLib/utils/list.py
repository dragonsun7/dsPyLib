# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-20 14:30:37'


# 去掉列表中的重复项(http://www.chenxm.cc/article/541.html)
def remove_duplicate(the_list: list):
    temp_list = list(set([str(j) for j in the_list]))
    the_list = [eval(j) for j in temp_list]
    return the_list
