# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2024-08-15 09:10:31'

from datetime import datetime, date, time, timedelta, timezone
from typing import Union, List

from dateutil.parser import parse, ParserError


def 转时间(时间: Union[datetime, date, str]) -> datetime:
    """
    将输入的日期时间对象或字符串转换为 datetime 对象。

    :param 时间: 输入的日期时间对象或字符串，可以是 datetime、date 或 str 类型。
    :return: 转换后的 datetime 对象。
    :raises ValueError: 如果输入类型不支持或字符串解析失败。
    """
    if isinstance(时间, datetime):
        return 时间
    elif isinstance(时间, date):
        return datetime.combine(时间, time(0, 0, 0))
    elif isinstance(时间, str):
        try:
            return parse(时间)
        except ParserError:
            raise ValueError(f'解析时间字符串失败，传入的字符串为：{时间}')
    raise ValueError('传入的时间类型必须为[[datetime, date, str]之一')


def 转时间列表(时间列表: list[Union[datetime, date, str]]) -> List[datetime]:
    """
    将输入的日期时间对象或字符串列表转换为 datetime 对象列表。

    :param 时间列表: 输入的日期时间对象或字符串列表。
    :return: 转换后的 datetime 对象列表。
    """
    return [转时间(时间=x) for x in 时间列表]


def 时间戳转标准时间(毫秒时间戳: int) -> datetime:
    """
    将毫秒时间戳转换为标准时间 (UTC)。

    :param 毫秒时间戳: 毫秒时间戳。
    :return: 转换后的 datetime 对象 (UTC)。
    """
    return datetime.fromtimestamp(毫秒时间戳 / 1000, tz=timezone.utc)


def 时间戳转北京时间(毫秒时间戳: int) -> datetime:
    """
    将毫秒时间戳转换为北京时间 (UTC+8)。

    :param 毫秒时间戳: 毫秒时间戳。
    :return: 转换后的 datetime 对象 (UTC+8)。
    """
    北京时区 = timezone(timedelta(hours=8))
    标准时间 = 时间戳转标准时间(毫秒时间戳=毫秒时间戳)
    北京时间 = 标准时间.astimezone(tz=北京时区)
    return 北京时间


def 时间转毫秒时间戳(时间: datetime) -> int:
    return int(时间.timestamp() * 1000)
