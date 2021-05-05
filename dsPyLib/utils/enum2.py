# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2021-05-05 17:00:03'

"""
    遍历枚举
"""


def get_enum_dict(enum_cls) -> dict:
    """
    输出枚举字典，{ 枚举名:枚举项, ... }
    :param enum_cls: 枚举类
    :return: 枚举字典
    """
    return enum_cls.__members__


def get_enum_attrs(enum_cls) -> list:
    """
    获取枚举类中的所有枚举项名称
    :param enum_cls: 枚举类
    :return: 枚举项名称列表
    """
    return list(get_enum_dict(enum_cls).keys())


def get_enum_items(enum_cls) -> list:
    """
    获取枚举类中的所有枚举项
    :param enum_cls: 枚举类
    :return: 枚举项列表
    """
    return list(get_enum_dict(enum_cls).values())


def get_enum_item_by_attr(enum_cls, attr: str):
    """
    根据枚举名，获取枚举项
    :param enum_cls: 枚举类
    :param attr: 枚举名
    :return: 枚举项
    """
    return get_enum_dict(enum_cls)[attr]


def get_enum_attr_by_item(enum_cls, item) -> str:
    """
    根据枚举项，获取枚举名
    :param enum_cls: 枚举类
    :param item: 枚举项
    :return: 枚举名
    """
    d = get_enum_dict(enum_cls)
    return list(d.keys())[list(d.values()).index(item)]
