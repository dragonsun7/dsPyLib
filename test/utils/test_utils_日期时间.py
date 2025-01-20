# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-07 00:18:09'

import unittest
from datetime import datetime, date, time, timedelta, timezone

# 导入待测试的函数
from dsPyLib.utils.日期时间 import 转时间, 转时间列表, 时间戳转标准时间, 时间戳转北京时间


class TestDateTimeFunctions(unittest.TestCase):

    def test_转时间_datetime(self):
        """
        测试 转时间 函数，输入为 datetime 类型。
        验证返回值是否与输入值一致。
        """
        now = datetime.now()
        result = 转时间(now)
        self.assertEqual(result, now)

    def test_转时间_date(self):
        """
        测试 转时间 函数，输入为 date 类型。
        验证返回值是否为当天的 datetime 对象（时间部分为 00:00:00）。
        """
        today = date.today()
        expected = datetime.combine(today, time(0, 0, 0))
        result = 转时间(today)
        self.assertEqual(result, expected)

    def test_转时间_str(self):
        """
        测试 转时间 函数，输入为有效的日期时间字符串。
        验证返回值是否为正确的 datetime 对象。
        """
        time_str = "2024-08-15 12:00:00"
        expected = datetime(2024, 8, 15, 12, 0, 0)
        result = 转时间(time_str)
        self.assertEqual(result, expected)

    def test_转时间_str_invalid(self):
        """
        测试 转时间 函数，输入为无效的日期时间字符串。
        验证是否抛出 ValueError 异常。
        """
        invalid_time_str = "无效时间"
        with self.assertRaises(ValueError):
            转时间(invalid_time_str)

    def test_转时间_invalid_type(self):
        """
        测试 转时间 函数，输入为不支持的类型（如 int）。
        验证是否抛出 ValueError 异常。
        """
        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            转时间(123)  # 输入为 int 类型

    def test_转时间列表(self):
        """
        测试 转时间列表 函数。
        输入为包含 str、date 和 datetime 的列表。
        验证返回值是否为正确的 datetime 对象列表。
        """
        input_list = ["2024-08-15 12:00:00", date(2024, 8, 15), datetime(2024, 8, 15, 12, 0, 0)]
        expected = [datetime(2024, 8, 15, 12, 0, 0), datetime(2024, 8, 15, 0, 0, 0), datetime(2024, 8, 15, 12, 0, 0)]
        result = 转时间列表(input_list)
        self.assertEqual(result, expected)

    def test_时间戳转标准时间(self):
        """
        测试 时间戳转标准时间 函数，输入为毫秒时间戳。
        验证返回值是否为正确的 UTC 时间。
        """
        from zoneinfo import ZoneInfo
        expected = datetime(2025, 1, 1, 0, 0, 0, tzinfo=ZoneInfo('UTC'))
        毫秒时间戳 = int(expected.timestamp()) * 1000
        print(毫秒时间戳, expected)
        result = 时间戳转标准时间(毫秒时间戳)
        self.assertEqual(result, expected)

    def test_时间戳转北京时间(self):
        """
        测试 时间戳转北京时间 函数，输入为毫秒时间戳。
        验证返回值是否为正确的北京时间（UTC+8）。
        """
        北京时区 = timezone(timedelta(hours=8))
        expected = datetime(2025, 1, 1, 0, 0, 0, tzinfo=北京时区)
        毫秒时间戳 = int(expected.timestamp()) * 1000
        print(毫秒时间戳, expected)
        result = 时间戳转北京时间(毫秒时间戳)
        self.assertEqual(result, expected)
