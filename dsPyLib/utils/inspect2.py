# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-10-22 21:38:16'

import inspect


# 获取当前函数名称
def get_current_function_name() -> str:
    return inspect.stack()[1][3]


# 获取对象属性名称列表(推荐使用：attr_names())
def get_attr_names(o, ignores: list[str] = None) -> list[str]:
    """
    获取对象属性名称列表
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


# 获取对象属性名称列表
def attr_names(o, exclude_base: bool = True, ignores: list[str] = None) -> list[str]:
    """
    获取对象属性名称列表(不包含私有)
    @param o: 对象
    @param exclude_base: 是否排除父类中的属性，默认True
    @param ignores: 要忽略的属性名称列表
    @return: 属性列表
    """
    if exclude_base:
        base = o.__class__.__base__()
        base_attrs = get_attr_names(o=base, ignores=ignores)
        attrs = get_attr_names(o=o, ignores=ignores)
        return list(set(attrs) - set(base_attrs))
    else:
        return get_attr_names(o=o, ignores=ignores)


# 生成对象属性名/属性值字典
def attr_to_dict(o, attrs: list[str]) -> dict:
    """
    生成对象属性名/属性值字典
    @param o: 对象
    @param attrs: 属性名列表
    @return: 字典，key为属性名，value为属性值
    """
    ret = dict()
    for key in attrs:
        ret[key] = getattr(o, key)
    return ret


# 通过列表数据为对象赋值
def attr_from_list(o, attrs: list[str], values: list):
    """
    通过列表数据为对象赋值
    @param o: 对象
    @param attrs: 属性名列表
    @param values: 属性值列表(需要与属性名列表一一对应)
    @return: 对象
    """
    for i, attr in enumerate(attrs):
        setattr(o, attr, values[i])
    return o


# 通过字典数据为对象赋值
def attr_from_dict(o, value: dict):
    """
    通过字典数据为对象赋值
    @param o: 对象
    @param value: 包含属性名/属性值的字典数据，其中key为属性名，value为属性值
    @return: 对象
    """
    attrs = list(value.keys())
    values = list(value.values())
    return attr_from_list(o=o, attrs=attrs, values=values)


# 通过另一个对象为对象赋值
def attr_from_object(o, src, attrs: list[str]):
    """
    通过另一个对象为对象赋值
    @param o: 对象
    @param src: 另一个对象，即数据来源
    @param attrs: 指定要参与赋值的属性名称列表
    @return: 对象
    """
    values = [getattr(src, attr) for attr in attrs]
    return attr_from_list(o=o, attrs=attrs, values=values)
