# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2024-01-27 19:08:47'

import datetime
import unittest

from dsPyLib.utils.datetimes import to_time


class TestToTime(unittest.TestCase):

    def setUp(self):
        self.now = datetime.datetime.now()
        self.time = self.now.time()

    def test_datetime(self):
        t1 = to_time(self.now).strftime('%H:%M:%S')
        t2 = self.time.strftime('%H:%M:%S')
        self.assertEqual(t1, t2)

    def test_time(self):
        t1 = to_time(self.time).strftime('%H:%M:%S')
        t2 = self.time.strftime('%H:%M:%S')
        self.assertEqual(t1, t2)

    def test_str(self):
        t1 = to_time('12:13:34')
        t2 = datetime.time(12, 13, 34)
        self.assertEqual(t1, t2)

    def test_错误的字符串(self):
        with self.assertRaises(ValueError):
            to_time(t='25:23:45')
