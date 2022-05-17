# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 21:59:01'

import unittest

from dsPyLib.utils.string import middle


class TestMiddle(unittest.TestCase):

    def test_空字符串(self):
        s = middle(s='', count=3)
        self.assertEqual(s, '')

    def test_数量_为负数(self):
        s = middle(s='123', count=-1)
        self.assertEqual(s, '')

    def test_奇数个字符串(self):
        s = middle(s='12345', count=3)
        self.assertEqual(s, '234')

    def test_偶数个字符串_左侧优先(self):
        s = middle(s='123456', count=3, left_first=True)
        self.assertEqual(s, '234')

    def test_偶数个字符串_右侧优先(self):
        s = middle(s='123456', count=3, left_first=False)
        self.assertEqual(s, '345')

    def test_长度_等于_零(self):
        s = middle(s='123456', count=0, left_first=False)
        self.assertEqual(s, '')

    def test_长度_大于_字符串长度(self):
        s = middle(s='123456', count=7, left_first=False)
        self.assertEqual(s, '123456')
