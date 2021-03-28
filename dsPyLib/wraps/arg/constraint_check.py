# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2021-03-27 12:36:36'

from functools import wraps
from inspect import signature

from .constraint import *


class ArgumentConstraintCheckerException(Exception):
    """
    约束检查异常类
    """

    def __init__(self, arg_name, code, msg):
        Exception.__init__(self)
        self.arg_name = arg_name
        self.code = code
        self.message = msg

    def __repr__(self):
        if self.arg_name:
            s = f"参数 '{self.arg_name}' {self.message} (code={self.code})"
        else:
            s = f"{self.message} (code={self.code})"
        return s

    __str__ = __repr__


class ConstraintCheck(object):
    """
    参数约束检查装饰类

    范例：
        from dsPyLib.wraps import arg

        @arg.ConstraintCheck(arg.ACUnsignedInt, arg.ACUnsignedInt)
        def foo(n1, n2):
            pass
    """

    def __init__(self, *wrap_args, **wrap_kwargs):
        self.wrap_args = wrap_args
        self.wrap_kwargs = wrap_kwargs

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            bound_constraints_cls = sig.bind_partial(*self.wrap_args, **self.wrap_kwargs).arguments
            try:
                bound_arguments = sig.bind(*args, **kwargs).arguments
            except TypeError:
                raise ArgumentConstraintCheckerException(arg_name='', code=-41, msg='参数不足')

            success = True
            name = ''
            code = 0
            msg = ''
            for name, constraint_cls in bound_constraints_cls.items():
                if not issubclass(constraint_cls, ArgumentConstraint):
                    code = -51
                    msg = '约束类不正确'
                    success = False
                    break

                if name not in bound_arguments:
                    code = -52
                    msg = '未传入值'
                    success = False
                    break

                value = bound_arguments[name]
                constraint = constraint_cls()
                if not constraint.check(value=value):
                    code = constraint.code
                    msg = constraint.message
                    success = False
                    break

            if not success:
                raise ArgumentConstraintCheckerException(arg_name=name, code=code, msg=msg)

            return func(*args, **kwargs)

        return wrapper
