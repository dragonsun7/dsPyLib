# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-10-22 21:38:16'

import inspect


# 获取当前函数名称
def get_current_function_name() -> str:
    return inspect.stack()[1][3]


def main():
    print(get_current_function_name())


if __name__ == '__main__':
    main()
