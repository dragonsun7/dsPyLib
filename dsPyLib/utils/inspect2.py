# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-10-22 21:38:16'

import inspect


# 获取当前函数名称
def get_current_function_name() -> str:
    return inspect.stack()[1][3]


# 获取当前对象属性列表
def get_attr_names(o, ignores: list = None) -> list:
    """
    获取对象自定义的属性列表
        1. 排除掉'_'和'__'打头的
        2. 排除掉'Meta'
        3. 排除掉方法
        4. 排除掉自定义忽略列表中的属性
    :return:
    """
    return [
        attr for attr in dir(o) if not (
                attr.startswith('_')  # 属性名不能以_开头，以_开头的为私有属性
                or attr.startswith('__')  # 属性名不能以__开头，以__开头的为私有属性
                or attr == 'Meta'  # 不考虑Meta属性
                or callable(getattr(o, attr))  # 不能为可调用的属性，可调用属性一般为方法
                or (ignores and (attr in ignores))
        )  # 不包含在自定义忽略列表中
    ]


# 获取不包含父类的属性列表
def get_attr_names_exclude_base(o, ignores: list = None) -> list:
    base = o.__class__.__base__()
    base_attrs = get_attr_names(o=base, ignores=ignores)
    attrs = get_attr_names(o=o, ignores=ignores)
    return list(set(attrs) - set(base_attrs))
