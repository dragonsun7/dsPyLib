# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2024-01-27 19:13:24'

import datetime
import unittest

from dsPyLib.utils.datetimes import to_time_str


class TestToTime(unittest.TestCase):

    def setUp(self):
        self.now = datetime.datetime.now()
        self.time = self.now.time()
        self.str = self.time.strftime('%H:%M:%S')

    def test_datetime(self):
        self.assertEqual(self.str, to_time_str(self.now))

    def test_time(self):
        self.assertEqual(self.str, to_time_str(self.time))

    def test_str(self):
        self.assertEqual(self.str, to_time_str(self.str))
