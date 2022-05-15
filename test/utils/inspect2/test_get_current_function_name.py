# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-15 19:49:00'

import unittest

from dsPyLib.utils.inspect2 import get_current_function_name


class TestInspect2GetCurrentFunctionName(unittest.TestCase):

    def test_get_current_function_name(self):
        s = get_current_function_name()
        self.assertEqual(s, 'test_get_current_function_name')
