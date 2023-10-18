# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-22 15:49:52'

import datetime
import unittest

from dsPyLib.utils.datetimes import last_month_day


class TestLastMonthDay(unittest.TestCase):

    def test_正常日期(self):
        expect = 31
        actual = last_month_day('2022-05-22')
        self.assertEqual(expect, actual)

    def test_闰年(self):
        expect = 29
        actual = last_month_day('2020-02-10')
        self.assertEqual(expect, actual)

    def test_非闰年(self):
        expect = 28
        actual = last_month_day('2021-02-10')
        self.assertEqual(expect, actual)

    def test_非正常值(self):
        expect = None
        actual = last_month_day(1)
        self.assertEqual(expect, actual)

    def test_None(self):
        expect = last_month_day(datetime.datetime.now())
        actual = last_month_day(None)
        self.assertEqual(expect, actual)
