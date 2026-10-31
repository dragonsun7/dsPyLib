# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-17 16:32:16'

import math
import re
import textwrap
import unicodedata
from enum import IntEnum


def 视觉长度(s: str) -> int:
    """
        计算字符串视觉宽度（粗略计算：中文算2，其他算1）

        unicodedata.east_asian_width(c)
            这是 Python 内置 unicodedata 模块提供的方法。它会返回字符 c 在 Unicode 东亚字符宽度属性 中的一个分类结果。
            这个分类是 Unicode 标准定义的，用来告诉系统该字符在东亚排版环境下的显示宽度。
            它返回的值主要有这几类：
                'W' (Wide)：宽字符（如绝大多数汉字、日文假名、韩文）。
                'F' (Fullwidth)：全角字符（如中文标点 ，、。，全角英文字母 Ａ）。
                'A' (Ambiguous)：歧义字符（在东亚环境通常算宽，在欧美环境算窄，如部分希腊字母、特殊符号）。
                'H' (Halfwidth)：半角字符（如日文片假名半角形式）。
                'Na' (Narrow)：窄字符（常规英文字母、数字、半角标点）。
                'N' (Neutral)：中性字符（如控制字符）。
    """
    return sum(2 if unicodedata.east_asian_width(c) in ('W', 'F') else 1 for c in s)


class 宽字符类(str):
    """
        继承 str，重写 __format__，让中文/全角字符按 2 个视觉宽度对齐。
        支持的格式：[[fill]align]width，例如 ">10"、"^6"、"*<8"。
        其他格式（精度、类型等）回落到 str.__format__。

        例如：
            names = ['三分钟', '一小时', '日']
            for a in name:
                logger.info(f'{宽字符类(a):>6}')

            会正确的处理中文字符的宽度问题
                2026-10-31 17:24:40,832[INFO]: <module>(1.py:47) 三分钟
                2026-10-31 17:24:40,832[INFO]: <module>(1.py:47) 一小时
                2026-10-31 17:24:40,832[INFO]: <module>(1.py:47)     日

        如果使用普通的str，就会出现右对齐不正确的情况
                logger.info(f'{a:>6}')
                    2026-10-31 17:29:30,630[INFO]: <module>(1.py:47)    三分钟
                    2026-10-31 17:29:30,630[INFO]: <module>(1.py:47)    一小时
                    2026-10-31 17:29:30,630[INFO]: <module>(1.py:47)      日

        格式模式解释：
            (?:(.)?([<^>]))?(\d+)
            │   │  │   │      │  │
            │   │  │   │      │  └─ ③ 一个或多个数字
            │   │  │   │      └──── ③ 捕获组：宽度
            │   │  │   └─────────── ② 捕获组：对齐符
            │   │  └─────────────── ① 捕获组：填充字符
            │   └────────────────── 非捕获组：把 ①② 打包
            └────────────────────── 让整个 ①② 可选

            描述的是 [[fill]align]width 这一小段语法，也就是 ">10"、"*>10"、"10" 这类格式串。
    """

    格式模式 = re.compile(r"(?:(.)?([<^>]))?(\d+)")

    def __format__(self, format_spec):
        """
            __format__ 是什么：
                当在 f-string 里写 f"{变量}" 时，Python 底层会调用 变量.__format__("")；
                写 f"{变量:>10}" 时，会调用 变量.__format__(">10")。
                这里的 format_spec 就是冒号后面的部分（比如 ">10"、"^6"）。
        """
        # 如果冒号后面什么都没写（即 f"{变量}"），那就没必要计算视觉宽度了，直接返回普通的字符串即可。
        if not format_spec:
            return str(self)

        # 解析对齐方式和目标宽度 (例如 ">10" 或 "^6")
        # ([<^>]?)：捕获 0 个或 1 个对齐符号（< 左对齐，^ 居中，> 右对齐）。
        # (\d+)：捕获 1 个或多个数字（代表目标宽度）。
        # 这个正则可以匹配 ">10"、"^6"，甚至也能匹配纯数字 "10"（此时对齐方式为空）。
        match = self.格式模式.fullmatch(format_spec)
        if not match:
            return super().__format__(format_spec)

        填充字符, 对齐方式, 目标宽度_str = match.groups()  # match.groups()：返回一个元组。例如输入 ">10"，返回 ('>', '10')。
        填充字符 = 填充字符 or ' '  # 默认用一个空格填充
        对齐方式 = 对齐方式 or ">"  # 默认右对齐
        目标宽度 = int(目标宽度_str)

        # 需要填充 = max(0, ...)：如果目标宽度是 10，当前文本视觉宽度是 8，则需要填充 2 个空格。
        # 加 max(0, ...) 是为了防止目标宽度比文本本身还窄时出现负数（负数会导致 " " * 负数 报错）。
        填充数量 = max(0, 目标宽度 - 视觉长度(self))

        # 根据对齐方式填充空格
        if 对齐方式 == ">":
            return 填充字符 * 填充数量 + str(self)
        if 对齐方式 == "<":
            return str(self) + 填充字符 * 填充数量
        if 对齐方式 == "^":
            左填充 = 填充数量 // 2
            右填充 = 填充数量 - 左填充
            return 填充字符 * 左填充 + str(self) + 填充字符 * 右填充

        return str(self)


# -------------------------------------------------------------------------------- #

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
