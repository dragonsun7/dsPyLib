# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-07 18:45:07'

import unittest
from dataclasses import dataclass

from dsPyLib.基类.模型基类 import 模型基类


class Test从对象导入(unittest.TestCase):

    def test_从对象导入(self):
        @dataclass
        class 测试模型(模型基类):
            属性1: str = '默认值'
            属性2: int = 0

        class 源对象:
            def __init__(self):
                self.属性1 = '新值1'
                self.属性2 = 10

        源实例 = 源对象()
        模型实例 = 测试模型().从对象导入(源实例)
        self.assertEqual(模型实例.属性1, '新值1')
        self.assertEqual(模型实例.属性2, 10)
