# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-06-09 21:03:40'


def get_class(module_path: str, module_name: str, class_name: str):
    """
        获取模块中的类
        例如：
                from src.app.module import Class
            那么：
                module_path:    'src.app'
                module_name:    'module'
                class_name:     'Class'
    """
    import importlib
    path = f'{module_path}.{module_name}'
    module = importlib.import_module(path)
    cls = getattr(module, class_name)
    return cls
