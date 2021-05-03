# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-10-22 21:38:16'

import inspect


# 获取当前函数名称
def get_current_function_name() -> str:
    return inspect.stack()[1][3]


# 获取当前对象属性列表
def get_attr_names(o, ignores: list[str] = None) -> list[str]:
    """
    获取对象自定义的属性列表
        1. 排除掉'_'和'__'打头的
        2. 排除掉方法
        3. 排除掉自定义忽略列表中的属性
    :return:
    """

    def is_keep(x: str) -> bool:
        if x.startswith('_') or x.startswith('__'):
            return False
        if inspect.ismethod(getattr(o, x)):
            return False
        if ignores and (x in ignores):
            return False
        return True

    attrs = o.__dir__()
    ret = filter(is_keep, attrs)
    return list(ret)


def main():
    print(get_current_function_name())


if __name__ == '__main__':
    main()
