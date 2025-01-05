# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2024-12-29 15:28:35'

from dataclasses import dataclass, field
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')  # 定义泛型类型


@dataclass
class 堆栈类(Generic[T]):
    """堆栈数据结构类

    支持泛型，可以存储任意类型的数据
    提供基本的堆栈操作：压入、弹出、查看栈顶、判空等
    """
    数据: List[T] = field(default_factory=list)

    def 压入(self, 数据: T) -> None:
        """将数据压入堆栈顶部"""
        self.数据.append(数据)

    def 弹出(self) -> Optional[T]:
        """从堆栈顶部弹出数据，如果堆栈为空返回None"""
        if self.为空():
            return None
        return self.数据.pop()

    def 栈顶(self) -> Optional[T]:
        """查看堆栈顶部的数据，不移除，如果堆栈为空返回None"""
        if self.为空():
            return None
        return self.数据[-1]

    def 为空(self) -> bool:
        """判断堆栈是否为空"""
        return len(self.数据) == 0

    def 大小(self) -> int:
        """返回堆栈中元素的数量"""
        return len(self.数据)

    def 清空(self) -> None:
        """清空堆栈"""
        self.数据.clear()

    def 转列表(self) -> List[T]:
        """将堆栈转换为列表"""
        return self.数据.copy()
