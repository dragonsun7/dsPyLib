# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-06-07 00:50:14'

import unittest

from dsPyLib.utils.list import equally


class TestEqually(unittest.TestCase):

    def test_无元素_0(self):
        with self.assertRaises(AssertionError):
            list(equally(data=[], n=0))

    def test_无元素_n(self):
        actual = list(equally(data=[], n=2))
        expect = []
        self.assertEqual(expect, actual)

    def test_有元素_0(self):
        with self.assertRaises(AssertionError):
            list(equally(data=[1, 2, 3], n=0))

    def test_有元素_1(self):
        actual = list(equally(data=[1, 2, 3], n=1))
        expect = [[1], [2], [3]]
        self.assertEqual(expect, actual)

    def test_有元素_不够一份(self):
        actual = list(equally(data=[1, 2, 3], n=4))
        expect = [[1, 2, 3]]
        self.assertEqual(expect, actual)

    def test_有元素_正好能均分为多份(self):
        actual = list(equally(data=[1, 2, 3, 4, 5, 6], n=3))
        expect = [[1, 2, 3], [4, 5, 6]]
        self.assertEqual(expect, actual)

    def test_有元素_不能均分为多份(self):
        actual = list(equally(data=[1, 2, 3, 4, 5, 6, 7], n=3))
        expect = [[1, 2, 3], [4, 5, 6], [7]]
        self.assertEqual(expect, actual)
