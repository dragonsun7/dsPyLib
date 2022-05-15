# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-16 01:36:43'

import unittest
from pprint import pprint

from dsPyLib.utils.inspect2 import attr_from_object, attr_to_dict, attr_from_list
from .datas.color_enum import ColorEnum
from .datas.obj2 import TestObject2


class TestAttrFromObject(unittest.TestCase):

    def test(self):
        attrs = ['prop_dict', 'prop_float', 'prop_int', 'prop_list', 'prop_str', 'prop_enum']
        values = [{'这是键': '这是值'}, 3.33, 333, ['444', 4.44], '这是字符串', ColorEnum.yellow]
        src = attr_from_list(o=TestObject2(), attrs=attrs, values=values)
        o = attr_from_object(o=TestObject2(), src=src, attrs=attrs)
        d = attr_to_dict(o=o, attrs=attrs)
        pprint(d)
