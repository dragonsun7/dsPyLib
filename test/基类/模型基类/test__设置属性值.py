# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-07 18:49:00'

import unittest
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from dsPyLib.utils.日期时间 import 时间戳转北京时间
from dsPyLib.基类.模型基类 import 模型基类


class Test设置属性值(unittest.TestCase):

    def test_设置属性值(self):
        @dataclass
        class 测试模型(模型基类):
            属性1: datetime = datetime.now()
            属性2: Decimal = Decimal(0)
            属性3: str = '默认值'
            属性4: int = 0
            属性5: bool = False

        模型实例 = 测试模型()
        模型实例._设置属性值('属性1', datetime, '1633024800000')
        模型实例._设置属性值('属性2', Decimal, '10.5')
        模型实例._设置属性值('属性3', str, '新值')
        模型实例._设置属性值('属性4', int, '20')
        模型实例._设置属性值('属性5', bool, '1')

        self.assertEqual(模型实例.属性1, 时间戳转北京时间(1633024800000))
        self.assertEqual(模型实例.属性2, Decimal('10.5'))
        self.assertEqual(模型实例.属性3, '新值')
        self.assertEqual(模型实例.属性4, 20)
        self.assertEqual(模型实例.属性5, True)
