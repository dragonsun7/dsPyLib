# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 16:38:34'

import unittest

from dsPyLib.utils.string import aligned, TextAlignEnum


class TestAligned(unittest.TestCase):

    def setUp(self) -> None:
        self.value = '12345'
        self.width = 5

    def test_值为空字符串(self):
        s = aligned(s='', width=self.width)
        self.assertEqual(s, '     ')

    def test_未指定宽度(self):
        s = aligned(s=self.value)
        self.assertEqual(s, '12345')

    def test_宽度为0(self):
        s = aligned(s='12345', width=0)
        self.assertEqual(s, '')

    def test_宽度为负数(self):
        s = aligned(s='12345', width=-1)
        self.assertEqual(s, '')

    def test_指定的宽度_等于_值的宽度(self):
        s = aligned(s=self.value, width=self.width)
        self.assertEqual(s, '12345')

    def test_指定的宽度_大于_值的宽度_左对齐(self):
        s = aligned(s=self.value, width=self.width + 2, align=TextAlignEnum.left)
        self.assertEqual(s, '12345  ')

    def test_指定的宽度_大于_值的宽度_居中对齐_左右同宽(self):
        s = aligned(s=self.value, width=self.width + 2, align=TextAlignEnum.center)
        self.assertEqual(s, ' 12345 ')

    def test_指定的宽度_大于_值的宽度_居中对齐_左右不同宽_01(self):
        s = aligned(s=self.value, width=self.width + 1, align=TextAlignEnum.center)
        self.assertEqual(s, '12345 ')

    def test_指定的宽度_大于_值的宽度_居中对齐_左右不同宽_02(self):
        s = aligned(s=self.value, width=self.width + 3, align=TextAlignEnum.center)
        self.assertEqual(s, ' 12345  ')

    def test_指定的宽度_大于_值的宽度_右对齐(self):
        s = aligned(s=self.value, width=self.width + 2, align=TextAlignEnum.right)
        self.assertEqual(s, '  12345')

    def test_指定的宽度_小于_值的宽度_左对齐(self):
        s = aligned(s=self.value, width=self.width - 2, align=TextAlignEnum.left)
        self.assertEqual(s, '123')

    def test_指定的宽度_小于_值的宽度_居中对齐_左右同宽(self):
        s = aligned(s=self.value, width=self.width - 2, align=TextAlignEnum.center)
        self.assertEqual(s, '234')

    def test_指定的宽度_小于_值的宽度_居中对齐_左右不同宽_01(self):
        s = aligned(s=self.value, width=self.width - 1, align=TextAlignEnum.center)
        self.assertEqual(s, '1234')

    def test_指定的宽度_小于_值的宽度_居中对齐_左右不同宽_02(self):
        s = aligned(s=self.value, width=self.width - 3, align=TextAlignEnum.center)
        self.assertEqual(s, '23')

    def test_指定的宽度_小于_值的宽度_右对齐(self):
        s = aligned(s=self.value, width=self.width - 2, align=TextAlignEnum.right)
        self.assertEqual(s, '345')
