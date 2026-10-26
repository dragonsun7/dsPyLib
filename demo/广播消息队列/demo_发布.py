# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-10-26 17:27:58'

import time

from dsConfigCenter import config_center

from dsPyLib.mqueue.mq_fanout import 广播发布者类
from dsPyLib.utils.logging import logger


def 发布任务():
    数据 = [
        {'desc': 'int', 'data': 99},
        {'desc': 'float', 'data': 88.88},
        {'desc': 'bool', 'data': True},
        {'desc': 'str', 'data': '你好'},
        {'desc': 'list', 'data': ['你好', 99, 88.88, None]},
        {'desc': 'dict', 'data': {'姓名': '张三', '年龄': 22, '体重': 33.33, }},
        {'desc': 'object', 'data': object()},
        {'desc': 'bytes', 'data': b"hello"},
        {'desc': 'None', 'data': None},
    ]

    循环量 = 0
    数据长度 = len(数据)
    while True:
        索引 = 循环量 % 数据长度
        数据项 = 数据[索引]
        result1 = 发布者.发布(desc=数据项['desc'], data=数据项['data'])
        if result1.is_err():
            e1 = result1.unwrap_err()
            logger.error(f'发布消息错误：{数据项}, {e1}')
        循环量 += 1
        time.sleep(1)


if __name__ == '__main__':
    消息队列配置 = config_center.get_rabbitmq(host='ali-hk')
    发布者 = 广播发布者类(配置=消息队列配置, virtual_host='Crypto', exchange_name='crypto.fanout')
    try:
        result = 发布者.连接()
        if result.is_err():
            e = result.unwrap_err()
            logger.error(f'发布者连接错误：{e}')
            raise SystemExit(-1)

        发布任务()
    finally:
        发布者.断开()
