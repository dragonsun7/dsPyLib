# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-24 20:16:25'

import unittest

from dsPyLib.utils.datetime import week_name_cn


class TestWeekNameCN(unittest.TestCase):

    def test_星期一(self):
        self.assertEqual('星期一', week_name_cn('2022-05-16'))

    def test_星期二(self):
        self.assertEqual('星期二', week_name_cn('2022-05-17'))

    def test_星期三(self):
        self.assertEqual('星期三', week_name_cn('2022-05-18'))

    def test_星期四(self):
        self.assertEqual('星期四', week_name_cn('2022-05-19'))

    def test_星期五(self):
        self.assertEqual('星期五', week_name_cn('2022-05-20'))

    def test_星期六(self):
        self.assertEqual('星期六', week_name_cn('2022-05-21'))

    def test_星期日(self):
        self.assertEqual('星期日', week_name_cn('2022-05-22'))
