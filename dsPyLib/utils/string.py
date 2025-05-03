# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 16:32:16'

import math
import textwrap
from enum import IntEnum


def half_split(s: str, left_first: bool = True) -> (str, str):
    """
    将字符串均分为两份
        例如：
            '123456' => '123', '456'
            '12345', 左侧优先 => '123', '45'
            '12345', 右侧优先 => '12', '345'
    @param s: 要均分的字符串
    @param left_first: True - 左侧优先。当为长度为单数时，左侧字符串要多一个； False - 右侧优先
    @return: (左侧字符串, 右侧字符串)
    """
    pos = math.ceil(len(s) / 2) if left_first else int(len(s) / 2)
    return s[:pos], s[pos:]


def middle(s: str, count: int, left_first: bool = True) -> str:
    """
    取字符串居中指定长度的字符
        例如：
            '12345', 3 => '234'
            '123456', 3, 左侧优先 => '234'
            '123456', 3, 右侧优先 => '345'
    @param s: 字符串
    @param count: 要获取的长度
    @param left_first: True - 左侧优先; False - 右侧优先; 优先的意思是指，当长度为偶数时，哪边多取一个
    @return: 居中的字符串
    """
    count = max(count, 0)  # 规避width为负数的情况
    start = int((len(s) - count) / 2) if left_first else math.ceil((len(s) - count) / 2)
    start = max(start, 0)
    end = start + count
    return s[start:end]


class TextAlignEnum(IntEnum):
    left = 0
    center = 1
    right = 2


def aligned(s: str, width: int = None, align: TextAlignEnum = TextAlignEnum.left) -> str:
    """
    生成对齐后的字符串
    例如：
        str_to_align(123, 5, TextAlignEnum.left)  => '123  '
        str_to_align(123, 5, TextAlignEnum.center)  => ' 123 '
        str_to_align(123, 5, TextAlignEnum.right) => '  123'
    @param s: 要生成字符串的值
    @param width: 生成的字符串宽度，如果未None则不限；如果不足，则左对齐截尾部，右对齐截头部
    @param align: 对齐方式
    @return:
    """
    s_width = len(s)  # 传入值的长度
    width = s_width if width is None else width  # 返回结果的长度
    width = max(width, 0)  # 规避width为负数的情况
    space_width = max(width - s_width, 0)  # 空格的个数
    space = ' ' * space_width  # 空格字符串

    # 生成背景字符串
    if align == TextAlignEnum.left:
        back = s + space
        return back[:width]
    elif align == TextAlignEnum.right:
        back = space + s
        return back[-width:]
    else:
        l, r = half_split(space, left_first=False)
        back = l + s + r
        return middle(s=back, count=width, left_first=True)


def 整体添加缩进(s: str, 制表符数: int) -> str:
    """
    针对多行的文本，前面整体添加缩进
    @param s:
    @param 制表符数: 每一行添加制表符的数量
    @return:
    """
    prefix = ''
    for i in range(制表符数):
        prefix += '\t'

    return textwrap.indent(text=s, prefix=prefix)
