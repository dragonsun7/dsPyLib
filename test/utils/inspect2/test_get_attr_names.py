# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-15 19:53:15'

import unittest

from dsPyLib.utils.inspect2 import get_attr_names
from .datas.obj1 import TestObject1
from .datas.obj2 import TestObject2


class TestGetAttrNames(unittest.TestCase):

    def test_父类无属性(self):
        names = ['prop_float', 'prop_int', 'prop_str']
        attrs = get_attr_names(o=TestObject1())
        self.assertEqual(set(names), set(attrs))

    def test_父类有属性(self):
        names = ['prop_dict', 'prop_float', 'prop_int', 'prop_list', 'prop_str', 'prop_enum']
        attrs = get_attr_names(o=TestObject2())
        self.assertEqual(set(names), set(attrs))

    def test_带忽略列表(self):
        names = ['prop_dict', 'prop_list', 'prop_str', 'prop_enum']
        ignores = ['prop_float', 'prop_int']
        attrs = get_attr_names(o=TestObject2(), ignores=ignores)
        self.assertEqual(set(names), set(attrs))
