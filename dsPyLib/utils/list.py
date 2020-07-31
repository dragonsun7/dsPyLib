# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-20 14:30:37'


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


if __name__ == '__main__':
    list1 = [1, 2, 1, 3, 2, 4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 9, 8, 0, 9]
    list2 = remove_duplicate2(list1)
    print(list2)
