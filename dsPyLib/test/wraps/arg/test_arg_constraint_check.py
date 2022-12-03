# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2021-03-26 13:57:48'

import unittest

from dsPyLib.wraps import arg


@arg.ConstraintCheck(arg.ACIsUnsignedInt, arg.ACIsUnsignedInt)
def foo(n1, n2):
    return n1, n2


class TestArgumentUnsignedIntTest(unittest.TestCase):

    # 参数正常
    def test_args_normal(self):
        foo(0, 1)

    # 参数不存在
    def test_args_not_exists(self):
        with self.assertRaises(arg.ArgumentConstraintCheckerException) as e:
            foo(s='')
        print(e.exception)

    # 参数不足
    def test_args_not_enough(self):
        with self.assertRaises(arg.ArgumentConstraintCheckerException) as e:
            foo(n1=0)
        print(e.exception)

    # 类型错误(None)
    def test_type_error_none(self):
        with self.assertRaises(arg.ArgumentConstraintCheckerException) as e:
            foo(1, None)
        print(e.exception)

    # 类型错误(str)
    def test_type_error_str(self):
        with self.assertRaises(arg.ArgumentConstraintCheckerException) as e:
            foo('-1', dict())
        print(e.exception)
