# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-15 19:53:37'

from .obj1 import TestObject1


class TestObject2(TestObject1):

    def __init__(self):
        super(TestObject2, self).__init__()
        self.prop_list = [1, '2']
        self.prop_dict = {'key1': 1, 'key2': '2'}
