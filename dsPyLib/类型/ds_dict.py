# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-19 23:51:35'

from typing import TypeVar, Type

from glom import glom, PathAccessError
from pydantic import BaseModel, ValidationError

from dsPyLib.类型.ds_rust_style_result import Result, Ok, Err

T = TypeVar('T')
MT = TypeVar('MT', bound=BaseModel)


def get_dict_value(data: dict, keypath: str, expected_type: Type[T]) -> Result[T, Exception]:
    """
    从字典中获取指定类型的值，失败时返回异常

    Args:
        data: 源字典
        keypath: 点号分隔的路径，如 'user.address.city'
        expected_type: 期望返回的类型

    Returns:
        Result[T, Exception]: 成功返回 Ok(转换后的值), 失败返回 Err(异常)

    Examples:
        >>> data1 = {'user': {'name': 'Alice', 'age': '25'}}
        >>> get_dict_value(data1, 'user.name', str)
        Ok('Alice')
        >>> get_dict_value(data1, 'user.age', int)
        Ok(25)
        >>> get_dict_value(data1, 'user.missing', str).is_err()
        True
    """
    try:
        value = glom(data, (keypath, expected_type))
        return Ok(value)
    except PathAccessError as e:  # key 不存在
        return Err(e)
    except (TypeError, ValueError) as e:  # 类型转换失败
        return Err(e)


def dict_to_model(data: dict, model_class: Type[MT]) -> Result[MT, Exception]:
    """
    创建模型对象，并用字典中的值初始化

    Args:
        data: 字典
        model_class: 模型类

    Returns:
        Result[MT, Exception]: 成功返回模型类的实例, 失败返回异常对象

    Examples:
        >>> class 用户(BaseModel):
        ...     name: str
        ...     age: int
        >>> dict_to_model({'name': 'Alice', 'age': 30}, 用户)
        Ok(用户(name='Alice', age=30))
        >>> dict_to_model({'name': 'Alice'}, 用户).is_err()
        True
        >>> dict_to_model({'name': 'Alice', 'age': 'abc'}, 用户).is_err()
        True
    """
    try:
        return Ok(model_class(**data))
    except (TypeError, ValidationError) as e:
        return Err(e)
