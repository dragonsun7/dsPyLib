# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-16 01:33:16'

import unittest
from pprint import pprint

from dsPyLib.utils.inspect2 import attr_from_dict, attr_to_dict
from .datas.color_enum import ColorEnum
from .datas.obj2 import TestObject2


class TestAttrFromDict(unittest.TestCase):

    def test(self):
        o = TestObject2()
        value = {
            'prop_dict': {'这是键': '这是值'},
            'prop_float': 3.33,
            'prop_int': 333,
            'prop_list': ['444', 4.44],
            'prop_str': '这是字符串',
            'prop_enum': ColorEnum.yellow,
        }
        o = attr_from_dict(o=o, value=value)
        d = attr_to_dict(o=o, attrs=list(value.keys()))
        pprint(d)
