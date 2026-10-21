# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2024-08-15 09:10:31'

from datetime import datetime, date, time, timedelta, timezone, tzinfo
from typing import Union, List, TypeAlias
from zoneinfo import ZoneInfo

from dateutil.parser import parse, ParserError

时间类型: TypeAlias = Union[datetime, date, str]

上海时区 = ZoneInfo("Asia/Shanghai")


def 转时间(时间: 时间类型, 时区: tzinfo = 上海时区) -> datetime:
    """
    将输入的日期时间对象或字符串转换为 datetime 对象，统一为指定时区（默认上海时区）。

        支持输入 datetime
        支持输入 date -> 转换为 0点的datetime
        支持输入日期字符串：
            '2024-01-01 12:00:00'
            '2024-01-01T12:00:00+08:00'
            '2024-01-01T04:00:00Z'

    :param 时间: 输入的日期时间对象或字符串，可以是 datetime、date 或 str 类型
    :param 时区: 输出时间的时区
    :return: 转换后的 datetime 对象。
    :raises ValueError: 如果输入类型不支持、时区为 None、解析时间字符串失败。
    """
    if 时区 is None:
        raise ValueError('时区不能为 None')

    if isinstance(时间, datetime):  # datetime需要在date前面判断，因为datetime是date的子类
        return 时间.astimezone(tz=时区) if 时间.tzinfo else 时间.replace(tzinfo=时区)

    if isinstance(时间, date):
        return datetime.combine(时间, time(0, 0, 0), tzinfo=时区)

    if isinstance(时间, str):
        try:
            结果 = parse(时间)
            return 结果.astimezone(tz=时区) if 结果.tzinfo else 结果.replace(tzinfo=时区)
        except ParserError as e:
            raise ValueError(f'解析时间字符串失败，传入的字符串为：{时间}') from e

    raise ValueError(f'传入的时间类型必须为[datetime, date, str]之一，实际为 {type(时间).__name__}')


def 转时间列表(时间列表: list[时间类型]) -> List[datetime]:
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


def 获取时长字符串(开始时间: datetime) -> str:  # 小时:分钟:秒
    开始 = 开始时间.replace(tzinfo=None)  # now()不带时区，不能和带时区的做运算
    结束 = datetime.now()
    时长: timedelta = 结束 - 开始
    总秒数 = 时长.total_seconds()
    小时数 = int(总秒数 // 3600)
    分钟数 = int((总秒数 % 3600) // 60)
    秒数 = int(总秒数 % 60)
    时长字符串 = f'{小时数}:{分钟数:02}:{秒数:02}'
    return 时长字符串
