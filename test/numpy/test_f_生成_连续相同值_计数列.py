# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-06-10 10:43:10'

import unittest

import numpy

from dsPyLib.numpy.f_生成_连续相同值_计数列 import 生成_连续相同值_计数列


class Test_f_生成_连续相同值_计数列(unittest.TestCase):

    def test_值序列_空(self):
        值序列 = []
        实际值 = 生成_连续相同值_计数列(值序列=numpy.array(值序列))
        期望值 = []
        self.assertTrue(numpy.array_equal(期望值, 实际值))

    def test_值序列_1(self):
        值序列 = [5]
        期望值 = [1]
        实际值 = 生成_连续相同值_计数列(值序列=numpy.array(值序列))
        self.assertTrue(numpy.array_equal(期望值, 实际值))

    def test_值序列_多(self):
        值序列 = [3, 3, 3, 4, 6, 6, 6, 6]
        期望值 = [1, 2, 3, 1, 1, 2, 3, 4]
        实际值 = 生成_连续相同值_计数列(值序列=numpy.array(值序列))
        self.assertTrue(numpy.array_equal(实际值, 期望值))
