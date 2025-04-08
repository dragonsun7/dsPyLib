# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2025-04-08 09:03:48'


def 验证键存在(字典: dict, 键名: list[str]):
    键名集合 = set(键名)
    键名存在 = 键名集合.issubset(字典.keys())
    if not 键名存在:
        不存在的键名 = list(键名集合 - 字典.keys())
        raise ValueError(f'字典中不存在必要的键：「{", ".join(不存在的键名)}」！')
