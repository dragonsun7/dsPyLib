# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2024-01-26 22:01:14'

import datetime
import unittest

from dsPyLib.utils.datetimes import to_date, to_datetime_str


class TestToDatetime(unittest.TestCase):

    def setUp(self):
        self.now = datetime.datetime.now()
        self.date = self.now.date()

    def test_datetime(self):
        self.assertEqual(self.date, to_date(d=self.now))

    def test_date(self):
        self.assertEqual(self.date, to_date(d=self.date))

    def test_str(self):
        self.assertEqual(self.date, to_date(d=to_datetime_str(d=self.date)))
        self.assertEqual(self.date, to_date(d=to_datetime_str(d=self.now, fmt='%Y-%m-%d %H:%M:%S')))

    def test_错误的字符串(self):
        with self.assertRaises(ValueError):
            to_date(d='20245-123-456')
