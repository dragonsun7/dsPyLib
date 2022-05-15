# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-15 19:53:37'

from .color_enum import ColorEnum
from .obj1 import TestObject1


class TestObject2(TestObject1):

    def __init__(self):
        super(TestObject2, self).__init__()
        self.prop_enum = ColorEnum.red
        self.prop_list = [
            1,
            '2',
            {'key1': 1, 'key2': '2'},
            TestObject1(),
            ColorEnum.yellow
        ]
        self.prop_dict = {
            'key1': 1,
            'key2': '2',
            'key3': self.prop_list,
            'key4': {'key1': 1, 'key2': '2'},
            'key5': ColorEnum.red,
        }
