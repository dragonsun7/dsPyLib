# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-16 01:17:03'

import unittest
from pprint import pprint

from dsPyLib.utils.inspect2 import attr_from_list, attr_to_dict
from .datas.color_enum import ColorEnum
from .datas.obj2 import TestObject2


class TestAttrFromList(unittest.TestCase):

    def test(self):
        o = TestObject2()
        attrs = ['prop_dict', 'prop_float', 'prop_int', 'prop_list', 'prop_str', 'prop_enum']
        values = [{'这是键': '这是值'}, 3.33, 333, ['444', 4.44], '这是字符串', ColorEnum.yellow]
        o = attr_from_list(o=o, attrs=attrs, values=values)
        d = attr_to_dict(o=o, attrs=attrs)
        pprint(d)
