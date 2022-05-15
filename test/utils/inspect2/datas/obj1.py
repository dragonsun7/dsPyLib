# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-15 19:53:29'


class TestObject1(object):

    class Meta:
        prop_meta = 'meta'

    def __init__(self):
        self.prop_int: int = 2
        self.prop_str: str = '22'
        self.prop_float: float = 2.22
