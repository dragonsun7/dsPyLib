# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2021-03-28 21:34:13'


# 基类
class ArgumentConstraint(object):

    def __init__(self):
        self.code = 0
        self.message = ''

    def check(self, value) -> bool:
        raise NotImplementedError()


# 无符号整型
class ACUnsignedInt(ArgumentConstraint):

    def check(self, value) -> bool:
        if not isinstance(value, int):
            self.code = -101
            self.message = '必须为int类型'
            return False
        if value < 0:
            self.code = -102
            self.message = '值必须大于等于0'
            return False
        return True


# 不能为None的Str
class ACNotNoneStr(ArgumentConstraint):

    def check(self, value) -> bool:
        if not isinstance(value, str):
            self.code = -111
            self.message = '必须为str类型'
            return False
        return True
