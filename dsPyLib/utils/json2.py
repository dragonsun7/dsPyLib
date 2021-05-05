# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-20 18:43:47'

import json


def get_pretty_json(data) -> str:
    """
    生成漂亮的json字符串
    :param data: 数据对象
    :return: str
    """
    # sort_keys: key排序
    # indent: 缩进4个空格
    # separators: 去掉指定字符后的空格
    # ensure_ascii: 是否按照ASCII输出(中文需要指定为False)
    json_str = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    # 上一句指定了ensure_ascii=False就不需要下面这句了
    # json_str = json_str.encode('utf-8').decode('unicode_escape')
    return json_str


def load_json_from_file(file: str) -> dict or list:
    """
    从Json文件中加载Json对象
    :param file:
    :return:
    """
    with open(file, 'r', encoding='utf8') as fp:
        return json.load(fp)


if __name__ == '__main__':
    obj = [
        {
            'open': 9659.5,
            'high': 9664.91,
            'low': 9650.0,
            'close': 9650.0,
            'volume': 2447.0,
            'currency_volume': 25.3276,
            'memo': '这是一条K线数据',
        }
    ]

    ret = get_pretty_json(data=obj)
    print(ret)
