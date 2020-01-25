# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-01-25 21:10:02'

import pandas


def get_col_index(df: pandas.DataFrame, col_name: str) -> int or None:
    """
    获取指定的列名在DataFrame中的索引
    :param df: DataFrame
    :param col_name: 列名
    :return: 如果有指定的列，返回对应的列索引; 如果没有指定的列，返回None
    """
    cols = list(df.columns)
    try:
        ret = cols.index(col_name)
    except ValueError:
        ret = None
    return ret


def is_col_exists(df: pandas.DataFrame, col_name: str) -> bool:
    """
    返回指定的列是否在DataFrame中存在
    :param df: DataFrame
    :param col_name: 列名
    :return: True - 列存在; False - 列不存在
    """
    index = get_col_index(df, col_name)
    ret = (index is not None)
    return ret
