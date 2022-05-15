# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-15 23:11:24'

import unittest

from dsPyLib.utils.inspect2 import attr_names
from .datas.obj2 import TestObject2


class TestAttrNames(unittest.TestCase):

    def test_包含父类的属性(self):
        names = ['prop_dict', 'prop_float', 'prop_int', 'prop_list', 'prop_str', 'prop_enum']
        attrs = attr_names(o=TestObject2(), exclude_base=False)
        self.assertEqual(set(names), set(attrs))

    def test_不包含父类的属性(self):
        names = ['prop_list', 'prop_dict', 'prop_enum']
        attrs = attr_names(o=TestObject2(), exclude_base=True)
        self.assertEqual(set(names), set(attrs))
