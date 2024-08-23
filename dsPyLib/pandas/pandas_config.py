# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-06-28 21:47:04'

import pandas

# 设置中文列头对齐：
#   https://zhuanlan.zhihu.com/p/497233470
#   https://bbs.quantclass.cn/thread/2269  **
#   https://blog.csdn.net/weekdawn/article/details/81389865

# 显示所有列
pandas.set_option('display.max_columns', None)
# 显示所有行
pandas.set_option('display.max_rows', None)
# 一行的宽度
pandas.set_option('display.width', None)
# 列的最大宽度
pandas.set_option('max_colwidth', 50)
# 列头居左对齐
pandas.set_option('display.colheader_justify', 'center')
# 如果 DataFrame 的列数超过屏幕宽度，输出将不会换行，而是压缩在一行中显示，可能会在末尾添加省略号（...）以表示内容被截断。
pandas.set_option('expand_frame_repr', False)

# 中文列头对齐
# （Pandas v0.23.4 官方中文文档）：https://www.bookstack.cn/read/pandas-0.23.4-zh/543fee809de88568.md
#
# 部分东亚国家/地区使用宽度相当于两个拉丁字符的 Unicode 字符。如果 DataFrame 或 Series 包含这些字符，则默认输出模式可能无法正确对齐它们。
# 启用此选项将影响 DataFrame 和 Series 的打印性能（大约慢 2 倍）。仅在实际需要时使用。
#
# 启用此选项display.unicode.east_asian_width可让 pandas 检查每个字符的“东亚宽度”属性。通过将此选项设置为 True，可以正确对齐这些字符。
#
# 此外，宽度为“模糊”的 Unicode 字符可能为 1 个字符或 2 个字符宽，具体取决于终端设置或编码。可以使用选项 display.unicode.ambiguous_as_wide 来处理模糊性。
#
# PyCharm编辑器设置，设置→编辑器→配色方案→控制台字体
# 将Font选择常规中文字库（如SimHei, SimSong等），字体大小设置偶数（如14，16等）即可，原因见上述代码注释，因为东亚地区，如中国，日本等地使用的是两个占位的Unicode字符
#
# 推荐字体：
#   更纱黑体
#       GitHub
#           https://github.com/be5invis/Sarasa-Gothic
#       版本选择
#           https://zhuanlan.zhihu.com/p/627059922
#       下载
#           发行版中的 SarasaMonoSC-TTF-1.0.19.7z
#       安装
#           SarasaMonoSC-Regular.ttf
#
pandas.set_option('display.unicode.ambiguous_as_wide', True)
pandas.set_option('display.unicode.east_asian_width', True)


# 为了防止IDE优化掉包引用
def pandas_do_nothing():
    pass
