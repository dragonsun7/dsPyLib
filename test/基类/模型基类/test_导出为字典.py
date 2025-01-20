# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-07 18:11:17'

import unittest
from collections import OrderedDict
from dataclasses import dataclass

from dsPyLib.基类.模型基类 import 模型基类


class Test导出为字典(unittest.TestCase):

    def test_导出为字典(self):
        @dataclass
        class 测试模型(模型基类):
            属性1: str = '值1'
            属性2: int = 2

        模型实例 = 测试模型()
        预期结果 = OrderedDict([('属性1', '值1'), ('属性2', 2)])
        self.assertEqual(模型实例.导出为字典(), 预期结果)
