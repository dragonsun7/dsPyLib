# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-15 20:37:03'

import unittest

from dsPyLib.utils.inspect2 import get_attr_names_exclude_base
from .datas.obj2 import TestObject2


class TestGetAttrNamesExcludeBase(unittest.TestCase):

    def test(self):
        names = ['prop_list', 'prop_dict']
        attrs = get_attr_names_exclude_base(o=TestObject2())
        self.assertEqual(set(names), set(attrs))
