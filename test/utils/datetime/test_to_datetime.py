# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-22 12:19:20'

import datetime
import unittest

from dsPyLib.utils.datetime import to_datetime


class TestToDatetime(unittest.TestCase):

    def test_仅指定参数d_日期时间类型(self):
        d = datetime.datetime(year=2022, month=5, day=22, hour=13, minute=12, second=11)
        ret = to_datetime(d)
        self.assertEqual(d, ret)

    def test_仅指定参数d_日期类型(self):
        d = datetime.date(year=2022, month=5, day=22)
        ret = to_datetime(d)
        self.assertEqual(d, ret)

    def test_仅指定参数d_字符串_有效日期时间(self):
        d = '2022-05-22 13:12:11'
        ret = to_datetime(d)
        self.assertEqual(datetime.datetime(year=2022, month=5, day=22, hour=13, minute=12, second=11), ret)

    def test_仅指定参数d_字符串_有效日期(self):
        d = '2022-05-22'
        ret = to_datetime(d)
        self.assertEqual(datetime.datetime(year=2022, month=5, day=22), ret)

    def test_仅指定参数d_非正常参数(self):
        ret = to_datetime(2)
        self.assertEqual(None, ret)

    def test_仅指定参数d_None(self):
        ret = to_datetime(None)
        self.assertEqual(None, ret)

    def test_指定了默认值_正常参数(self):
        d = '2022-05-22 13:12:11'
        ret = to_datetime(d, default=datetime.datetime.now())
        self.assertEqual(datetime.datetime(year=2022, month=5, day=22, hour=13, minute=12, second=11), ret)

    def test_指定了默认值_非正常参数(self):
        ret = to_datetime(None, default=datetime.datetime(year=2022, month=5, day=22, hour=13, minute=12, second=11))
        self.assertEqual(datetime.datetime(year=2022, month=5, day=22, hour=13, minute=12, second=11), ret)
