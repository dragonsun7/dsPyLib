# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2024-08-14 14:36:03'

from collections import OrderedDict
from dataclasses import dataclass, fields, asdict
from datetime import datetime
from decimal import Decimal
from typing import Type, Any, Union, List, TypeVar, Tuple

import pandas

from .枚举基类 import 枚举基类
from ..utils.日期时间 import 时间戳转北京时间

常量_映射键名 = '映射'
常量_忽略键名 = '忽略'

T = TypeVar('T', bound='模型基类')


@dataclass
class 模型基类(object):

    def 导出为字典(self) -> OrderedDict:
        属性名表 = [field.name for field in fields(self)]  # 按属性声明顺序
        对象字典 = asdict(self)
        return OrderedDict((属性名, 对象字典[属性名]) for 属性名 in 属性名表)  # 生成顺序字典

    def 从数据导入(self, 数据: Union[dict, list]) -> T:
        所有属性信息 = fields(self)
        属性名称列表 = [field.name for field in 所有属性信息]  # 按属性声明顺序
        属性类型列表 = [field.type for field in 所有属性信息]  # 按属性声明顺序
        映射键名列表 = [field.metadata.get(常量_映射键名, None) for field in 所有属性信息]  # 与属性对应
        忽略赋值列表 = [field.metadata.get(常量_忽略键名, False) for field in 所有属性信息]
        for 索引, 属性名称 in enumerate(属性名称列表):
            忽略赋值 = 忽略赋值列表[索引]
            if 忽略赋值:
                continue

            映射键名 = 映射键名列表[索引]
            if 映射键名 is None:  # 如果没有指定映射键名，也就意味着属性名和键名一致
                映射键名 = 属性名称

            属性类型 = 属性类型列表[索引]
            属性值 = 数据[映射键名] if isinstance(数据, dict) else 数据[索引]
            self._设置属性值(属性名=属性名称, 属性类型=属性类型, 属性值=属性值)
        return self  # 链式调用

    def 从对象导入(self, 对象) -> T:
        所有属性信息 = fields(self)
        属性名称列表 = [field.name for field in 所有属性信息]  # 按属性声明顺序
        属性类型列表 = [field.type for field in 所有属性信息]  # 按属性声明顺序
        for 索引, 属性名称 in enumerate(属性名称列表):
            if hasattr(对象, 属性名称):
                属性值 = getattr(对象, 属性名称)
                属性类型 = 属性类型列表[索引]
                self._设置属性值(属性名=属性名称, 属性类型=属性类型, 属性值=属性值)
        return self

    @classmethod
    def 数据列表转模型列表(cls, 数据列表: List[Union[dict, list]]) -> List[T]:
        return [cls().从数据导入(数据=数据) for 数据 in 数据列表]

    @classmethod
    def 模型列表转数据帧(cls, 模型列表: List[T]) -> pandas.DataFrame:
        字典列表 = (模型.导出为字典() for 模型 in 模型列表)  # 使用生成器表达式
        return pandas.DataFrame(data=字典列表)

    @classmethod
    def 数据集转模型列表(cls, 数据集: List[Any]) -> List[T]:
        return [cls().从对象导入(对象=x) for x in 数据集]

    # -------------------------------------------------------------------------------- #

    # 有时候设置属性值希望加入一些自定义处理，只需要在子类重写该方法即可
    # 返回值：(是否有新的属性值, 新的属性值)
    # 如果没有自定义处理属性值，则按照默认方式处理
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _自定义属性值处理(self, 属性名: str, 属性类型: Type, 属性值: Any) -> Tuple[bool, Any]:
        return False, None

    def _设置属性值(self, 属性名: str, 属性类型: Type, 属性值: Any):
        有新属性值, 新属性值 = self._自定义属性值处理(属性名=属性名, 属性类型=属性类型, 属性值=属性值)
        if 有新属性值:
            setattr(self, 属性名, 新属性值)
            return

        try:
            if 属性类型 == datetime:
                if isinstance(属性值, str):
                    属性值 = 时间戳转北京时间(int(属性值))
            elif 属性类型 == Decimal:
                属性值 = Decimal(属性值) if 属性值 else Decimal(-1.0)
            elif 属性类型 == float:
                try:
                    属性值 = float(属性值)
                except ValueError:
                    属性值 = -1.0
            elif 属性类型 == str:
                属性值 = str(属性值)
            elif 属性类型 == int:
                属性值 = 0 if 属性值 == '' else int(属性值)
            elif 属性类型 == bool:
                属性值 = True if 属性值 == '1' else False
            elif issubclass(属性类型, 枚举基类):
                属性值 = 属性类型(属性值)
            elif issubclass(属性类型, 模型基类):
                pass
            else:
                pass

            setattr(self, 属性名, 属性值)
        except (ValueError, TypeError) as e:
            raise ValueError(f"无法设置属性 '{属性名}' 的值: {e}")

        # list
        # 需要在list属性初始化时，放入一个元素用于判断类型
        # 例如：
        #   self.details: list[AssetModel] = [AssetModel()]
        # if t == list:
        #     if len(attr) == 1:  # 验证只有一个元素(因为只用放一个元素用于判断类型)
        #         attr = attr[0]
        #         t = type(attr)
        #         if isinstance(attr, BaseModel):
        #             lst = list()
        #             for x in value:
        #                 item = t().from_data(data=x)
        #                 lst.append(item)
        #             setattr(self, key, lst)
        #     return
