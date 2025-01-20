# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-01-07 18:56:40'

import unittest
from dataclasses import dataclass
from typing import Type, Any, Tuple

from dsPyLib.基类.模型基类 import 模型基类


class Test自定义属性值处理(unittest.TestCase):

    def test_自定义属性值处理(self):
        @dataclass
        class 测试模型(模型基类):
            属性1: str = '默认值'

            def _自定义属性值处理(self, 属性名: str, 属性类型: Type, 属性值: Any) -> Tuple[bool, Any]:
                if 属性名 == '属性1':
                    return True, '自定义值'
                return False, None

        模型实例 = 测试模型()
        模型实例._设置属性值('属性1', str, '原始值')
        self.assertEqual(模型实例.属性1, '自定义值')
