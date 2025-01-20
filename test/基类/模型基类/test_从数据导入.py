# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-07 18:13:12'

import unittest
from dataclasses import dataclass

from dsPyLib.基类.模型基类 import 模型基类


class Test从数据导入(unittest.TestCase):

    def test_从字典导入(self):
        @dataclass
        class 测试模型(模型基类):
            属性1: str = '默认值'
            属性2: int = 0

        数据 = {'属性1': '新值1', '属性2': 10}
        模型实例 = 测试模型().从数据导入(数据)
        self.assertEqual(模型实例.属性1, '新值1')
        self.assertEqual(模型实例.属性2, 10)

    def test_从列表导入(self):
        @dataclass
        class 测试模型(模型基类):
            属性1: str = '默认值'
            属性2: int = 0

        数据 = ['新值1', 10]
        模型实例 = 测试模型().从数据导入(数据)
        self.assertEqual(模型实例.属性1, '新值1')
        self.assertEqual(模型实例.属性2, 10)
