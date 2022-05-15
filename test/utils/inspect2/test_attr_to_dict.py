# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-15 23:40:45'

import unittest
from pprint import pprint

from dsPyLib.utils.inspect2 import attr_to_dict, attr_names
from .datas.obj2 import TestObject2


class TestAttrToDict(unittest.TestCase):

    def test(self):
        o = TestObject2()
        attrs = attr_names(o=o, exclude_base=False, ignores=None)
        d = attr_to_dict(o=o, attrs=attrs)
        pprint(d)
