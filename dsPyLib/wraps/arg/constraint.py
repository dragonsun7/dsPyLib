# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2021-03-28 21:34:13'

from numpy import ndarray
from pandas import Series


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


# 大于1的无符号整数
class ACNotZeroUnsignedInt(ACUnsignedInt):

    def check(self, value) -> bool:
        ret = super(ACNotZeroUnsignedInt, self).check(value=value)
        if ret:
            if value < 1:
                self.code = -102
                self.message = '值必须大于等于0'
                ret = False
        return ret


# 不能为None的Str
class ACNotNoneStr(ArgumentConstraint):

    def check(self, value) -> bool:
        if not isinstance(value, str):
            self.code = -201
            self.message = '必须为str类型'
            return False
        return True


# 不能为None的Series
class ACNotNonePandasSeries(ArgumentConstraint):

    def check(self, value) -> bool:
        if not isinstance(value, Series):
            self.code = -301
            self.message = '必须为pandas.Series类型'
            return False
        return True


# 不能为None也不能为空的Series
class ACNotNoneAndEmptyPandasSeries(ArgumentConstraint):

    def check(self, value) -> bool:
        if not isinstance(value, Series):
            self.code = -301
            self.message = '必须为pandas.Series类型'
            return False
        if value.empty:
            self.code = -302
            self.message = '不能为空数据'
            return False
        return True


# 不能为None也不能为空的ndarray
class ACNotNoneAndEmptyNumpyNdarray(ArgumentConstraint):

    def check(self, value) -> bool:
        if not isinstance(value, ndarray):
            self.code = -401
            self.message = '必须为numpy.ndarray类型'
            return False
        if value.size == 0:
            self.code = -402
            self.message = '不能为空数据'
            return False
        return True
