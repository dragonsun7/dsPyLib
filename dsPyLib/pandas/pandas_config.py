# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-06-28 21:47:04'

import pandas

# https://blog.csdn.net/weekdawn/article/details/81389865

# 显示所有列
pandas.set_option('display.max_columns', None)
# 显示所有行
pandas.set_option('display.max_rows', None)
# 一行的宽度
pandas.set_option('display.width', None)
# 设置value的显示长度为200，默认为50
pandas.set_option('max_colwidth', 200)
