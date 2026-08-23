# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-06-08 09:56:26'

import warnings

import pandas
import peewee

from dsPyLib.类型.ds_rust_style_result import Result, Ok, Err


# 从Peewee的Query中生成DataFrame
def query_to_df(query: peewee.ModelSelect) -> Result[pandas.DataFrame, Exception]:
    """
        warnings.filterwarnings('ignore', category=UserWarning)
        全局副作用，会污染调用方
        
        下面的写法局部化了
    """
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=UserWarning)

        try:
            connection = query._database.connection()  # noqa
            sql, params = query.sql()
            return Ok(pandas.read_sql_query(sql=sql, con=connection, params=params))
        except Exception as e:
            return Err(e)


def query_to_list(query: peewee.ModelSelect) -> Result[list[dict], Exception]:
    """
    将查询的结果集，转换为字典列表
    :param query: 查询结果集
    :return: list(dict)
    """
    try:
        return Ok(list(query.dicts()))
    except Exception as e:
        return Err(e)
