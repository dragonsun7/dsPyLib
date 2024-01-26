# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-22 12:19:20'

import datetime
import unittest

from dsPyLib.utils.datetimes import to_datetime, to_datetime_str


class TestToDatetime(unittest.TestCase):

    def setUp(self):
        self.now = datetime.datetime.now()
        self.date = self.now.date()

    def test_datetime(self):
        self.assertEqual(self.now, to_datetime(self.now))

    def test_date(self):
        self.assertEqual(to_datetime(self.now.date()), to_datetime(self.date))

    def test_str(self):
        self.assertEqual(to_datetime(self.now.date()), to_datetime(d=to_datetime_str(d=self.date)))

        s = to_datetime_str(self.now, fmt='%Y-%m-%d %H:%M:%S')
        d = self.now.replace(microsecond=0)
        self.assertEqual(d, to_datetime(d=s))

    def test_仅指定参数d_字符串_有效日期(self):
        with self.assertRaises(ValueError):
            to_datetime(d='20245-123-456')
