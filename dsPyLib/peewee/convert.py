# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-06-08 09:56:26'

import pandas
import peewee


# 从Peewee的Query中生成DataFrame
def data_frame_from_peewee_query(query: peewee.Query) -> pandas.DataFrame:
    connection = query._database.connection()  # noqa
    sql, params = query.sql()
    return pandas.read_sql_query(sql=sql, con=connection, params=params)


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
