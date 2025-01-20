# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-07 18:45:51'

import unittest
from dataclasses import dataclass

from dsPyLib.基类.模型基类 import 模型基类


class Test数据列表转模型列表(unittest.TestCase):

    def test_数据列表转模型列表(self):
        @dataclass
        class 测试模型(模型基类):
            属性1: str = '默认值'
            属性2: int = 0

        数据列表 = [{'属性1': '值1', '属性2': 1}, {'属性1': '值2', '属性2': 2}]
        模型列表 = 测试模型.数据列表转模型列表(数据列表)
        self.assertEqual(len(模型列表), 2)
        self.assertEqual(模型列表[0].属性1, '值1')
        self.assertEqual(模型列表[1].属性2, 2)
