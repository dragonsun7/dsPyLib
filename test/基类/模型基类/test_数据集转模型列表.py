# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-07 18:47:38'

import unittest
from dataclasses import dataclass

from dsPyLib.基类.模型基类 import 模型基类


class Test数据集转模型列表(unittest.TestCase):

    def test_数据集转模型列表(self):
        @dataclass
        class 测试模型(模型基类):
            属性1: str = '默认值'
            属性2: int = 0

        class 源对象:
            def __init__(self):
                self.属性1 = '新值1'
                self.属性2 = 10

        数据集 = [源对象(), 源对象()]
        模型列表 = 测试模型.数据集转模型列表(数据集)
        self.assertEqual(len(模型列表), 2)
        self.assertEqual(模型列表[0].属性1, '新值1')
