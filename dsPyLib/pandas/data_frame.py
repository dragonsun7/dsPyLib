# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-01-25 21:10:02'

from dsPyLib.pandas.pandas_config import *


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


def get_columns(df: pandas.DataFrame) -> list:
    """
    获取列名
        有三种方法：
            df.columns.values -> ndarray
            list(df) -> list
            df.columns.tolist() - list
    :param df:
    :return:
    """
    return df.columns.tolist()


def get_column_len_max(df: pandas.DataFrame, col_name: str) -> int:
    """
    返回指定列中最大的字符长度
    :param df:
    :param col_name
    :return:
    """
    return df[col_name].map(len).max()


def get_column_len_min(df: pandas.DataFrame, col_name: str) -> int:
    """
    返回指定列中最小的字符长度
    :param df:
    :param col_name
    :return:
    """
    return df[col_name].map(len).min()
