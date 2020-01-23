# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'

import datetime
import dateutil.parser as date_parser  # pip install python-dateutil


def timestamp_to_iso(ts):
    """
    将timestamp转换为ISO8601字符串
    例如：
        timestamp_to_iso(time.time()) => 2019-04-07T12:51:30.000Z
    :param ts: timestamp
    :return: str
    """
    date = datetime.datetime.utcfromtimestamp(ts)
    iso = date.isoformat('T', 'milliseconds') + 'Z'
    return iso


def iso_to_datetime(s: str) -> datetime.datetime:
    """
    将ISO8601字符串转换为datetime.datetime
    :param s: str, ISO8601字符串，例如：'2019-04-13T12:50:00.000Z'
    :return: datetime
    """
    return date_parser.parse(s)


def datetime_to_iso(d: datetime.datetime) -> str:
    """
    将datetime转换为ISO8601字符串
    :param d: datetime.datetime
    :return: str, ISO8601字符串，例如：'2019-04-13T12:50:00.000Z'
    """
    if d:
        d1 = datetime.datetime.utcfromtimestamp(d.timestamp())
        return d1.isoformat(timespec='milliseconds') + 'Z'
    else:
        return ''


def str_to_date(date_str: str, fmt: str = '%Y-%m-%d') -> datetime.date:
    """
    字符串转换为日期
    :param date_str: 日期字符串，要符合fmt指定的格式
    :param fmt: 日期字符串格式
    :return: 日期对象
    """
    ret = datetime.datetime.strptime(date_str, fmt)
    return ret


def date_to_str(d: datetime.date, fmt: str = '%Y-%m-%d') -> str:
    """
    日期转换为字符串
    :param d: 日期
    :param fmt: 日期字符串格式
    :return: 日期字符串
    """
    ret = d.strftime(fmt)
    return ret


def is_weekend(d: datetime.date) -> bool:
    """
    判断指定的日期是否为周末(周六、周日)
    :param d: 日期
    :return: True - 是；False - 否
    """
    weekday = d.weekday() + 1
    ret = ((weekday == 6) or (weekday == 7))
    return ret
