# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-01-25 21:10:02'

from prettytable import PrettyTable

from dsPyLib.pandas.pandas_config import *


def 转成表格字符串(df: pandas.DataFrame) -> str:
    """
    将DataFrame转化为漂亮的对齐的表格字符串
    @param df:
    @return:
    """
    表格 = PrettyTable()
    for 行 in df.values:
        表格.add_row(行)
    return 表格.get_string()


def 验证列存在(df: pandas.DataFrame, 列名: list[str]):
    传入的数据列 = df.columns.tolist()
    缺少的数据列 = list(set(列名) - set(传入的数据列))
    if 缺少的数据列:
        raise ValueError(f'数据列「{", ".join(缺少的数据列)}」不存在！')


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
