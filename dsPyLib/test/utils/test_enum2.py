# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2021-05-05 18:35:57'

import unittest
from enum import unique, Enum

from dsPyLib.utils.enum2 import *


@unique
class SampleEnum(Enum):
    red = '红色'
    yellow = '黄色'
    blue = '蓝色'


class TestEnum2(unittest.TestCase):

    def test_get_enum_dict(self):
        org = {
            'red': SampleEnum.red,
            'yellow': SampleEnum.yellow,
            'blue': SampleEnum.blue
        }
        enum_dict = get_enum_dict(SampleEnum)
        self.assertEqual(org, enum_dict)

    def test_get_enum_attrs(self):
        org = {'red', 'yellow', 'blue'}
        attrs = set(get_enum_attrs(SampleEnum))
        self.assertEqual(org, attrs)

    def test_get_enum_items(self):
        org = {SampleEnum.red, SampleEnum.yellow, SampleEnum.blue}
        items = set(get_enum_items(SampleEnum))
        self.assertEqual(org, items)

    def test_get_enum_item_by_attr(self):
        self.assertEqual(get_enum_item_by_attr(SampleEnum, 'red'), SampleEnum.red)
        self.assertEqual(get_enum_item_by_attr(SampleEnum, 'yellow'), SampleEnum.yellow)
        self.assertEqual(get_enum_item_by_attr(SampleEnum, 'blue'), SampleEnum.blue)

    def test_get_enum_attr_by_item(self):
        self.assertEqual(get_enum_attr_by_item(SampleEnum, SampleEnum.red), 'red')
        self.assertEqual(get_enum_attr_by_item(SampleEnum, SampleEnum.yellow), 'yellow')
        self.assertEqual(get_enum_attr_by_item(SampleEnum, SampleEnum.blue), 'blue')
