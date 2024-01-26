# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-06-28 21:47:04'

import pandas

# 设置中文列头对齐：
#   https://zhuanlan.zhihu.com/p/497233470
#   https://bbs.quantclass.cn/thread/2269
# https://blog.csdn.net/weekdawn/article/details/81389865

# 显示所有列
pandas.set_option('display.max_columns', None)
# 显示所有行
pandas.set_option('display.max_rows', None)
# 一行的宽度
pandas.set_option('display.width', None)
# 设置value的显示长度为200，默认为50
pandas.set_option('max_colwidth', 200)
# 中文列头对齐
pandas.set_option('display.unicode.ambiguous_as_wide', True)
pandas.set_option('display.unicode.east_asian_width', True)  # 输出右对齐
# 列头居中对齐
pandas.set_option('display.colheader_justify', 'center')


# 为了防止IDE优化掉包引用
def pandas_do_nothing():
    pass
