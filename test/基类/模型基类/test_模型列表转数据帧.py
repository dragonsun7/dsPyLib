# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-07 18:46:41'

import unittest
from dataclasses import dataclass

import pandas

from dsPyLib.基类.模型基类 import 模型基类


class Test模型列表转数据帧(unittest.TestCase):

    def test_模型列表转数据帧(self):
        @dataclass
        class 测试模型(模型基类):
            属性1: str = '默认值'
            属性2: int = 0

        模型列表 = [测试模型(属性1='值1', 属性2=1), 测试模型(属性1='值2', 属性2=2)]
        数据帧 = 测试模型.模型列表转数据帧(模型列表)
        self.assertIsInstance(数据帧, pandas.DataFrame)
        self.assertEqual(len(数据帧), 2)
        self.assertEqual(数据帧.iloc[0]['属性1'], '值1')
