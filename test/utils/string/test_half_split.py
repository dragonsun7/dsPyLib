# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 21:34:40'

import unittest

from dsPyLib.utils.string import half_split


class TestHalfSplit(unittest.TestCase):

    def test_空字符串(self):
        ret = half_split(s='')
        self.assertEqual(ret, ('', ''))

    def test_偶数个字符(self):
        ret = half_split(s='1234')
        self.assertEqual(ret, ('12', '34'))

    def test_只有一个字符_左侧优先(self):
        ret = half_split(s='1', left_first=True)
        self.assertEqual(ret, ('1', ''))

    def test_只有一个字符_右侧优先(self):
        ret = half_split(s='1', left_first=False)
        self.assertEqual(ret, ('', '1'))

    def test_奇数个字符_左侧优先(self):
        ret = half_split(s='12345', left_first=True)
        self.assertEqual(ret, ('123', '45'))

    def test_奇数个字符_右侧优先(self):
        ret = half_split(s='12345', left_first=False)
        self.assertEqual(ret, ('12', '345'))
