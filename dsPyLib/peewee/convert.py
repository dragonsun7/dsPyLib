# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-06-08 09:56:26'

import pandas


def query_to_list(query) -> list:
    """
    将查询的结果集，转换为字典列表
    :param query: 查询结果集
    :return: list(dict)
    """
    if query is None:
        return list()
    else:
        query = query.dicts()
        dicts = list()
        for rec in query:
            dicts.append(rec)
        return dicts


def query_to_df(query) -> pandas.DataFrame:
    """
    将查询的结果集，转换为DataFrame
    :param query: 查询结果集
    :return: pandas.DataFrame
    """
    the_list = query_to_list(query)
    ret = pandas.DataFrame(the_list)
    return ret
