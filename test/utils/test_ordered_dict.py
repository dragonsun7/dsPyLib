# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-06-16 03:04:41'

import unittest

from dsPyLib.utils.ordered_dict import equal_ordered_dict, OrderedDict


class Test_ordered_dict(unittest.TestCase):

    def test_元素都为0(self):
        d1 = OrderedDict()
        d2 = OrderedDict()
        self.assertTrue(equal_ordered_dict(d1, d2))

    def test_相同_无nan(self):
        d1 = OrderedDict([('a', 1), ('c', 3)])
        d2 = OrderedDict([('a', 1), ('c', 3)])
        self.assertTrue(equal_ordered_dict(d1, d2))

    def test_相同_有nan(self):
        d1 = OrderedDict([('a', 1), ('b', float('nan')), ('c', 3)])
        d2 = OrderedDict([('a', 1), ('b', float('nan')), ('c', 3)])
        self.assertTrue(equal_ordered_dict(d1, d2))

    def test_长度不一致(self):
        d1 = OrderedDict([('a', 1), ('b', float('nan')), ('c', 3)])
        d2 = OrderedDict([('a', 1), ('b', float('nan'))])
        self.assertFalse(equal_ordered_dict(d1, d2))

    def test_键名不一致(self):
        d1 = OrderedDict([('a', 1), ('b', float('nan')), ('c', 3)])
        d2 = OrderedDict([('a', 1), ('b', float('nan')), ('c1', 3)])
        self.assertFalse(equal_ordered_dict(d1, d2))

    def test_键值不一致(self):
        d1 = OrderedDict([('a', 1), ('b', float('nan')), ('c', 3)])
        d2 = OrderedDict([('a', 1), ('b', float('nan')), ('c', 2)])
        self.assertFalse(equal_ordered_dict(d1, d2))

    def test_顺序不一致(self):
        d1 = OrderedDict([('a', 1), ('b', float('nan')), ('c', 3)])
        d2 = OrderedDict([('a', 1), ('c', 3), ('b', float('nan'))])
        self.assertFalse(equal_ordered_dict(d1, d2))
