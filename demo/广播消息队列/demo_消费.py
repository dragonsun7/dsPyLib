# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-10-26 17:28:06'

import threading
from typing import Any

from dsConfigCenter import config_center

from dsPyLib.mqueue.mq_fanout import 广播消费者类, 断开类型枚举


def 消息回调处理(desc: str, data: Any) -> None:
    print(f'{desc}: {data}')


def 连接成功回调处理() -> None:
    print('绿灯亮起来')


def 连接断开回调处理(断开类型: 断开类型枚举, 原因: Exception) -> None:
    print(f'红灯亮起来, {断开类型.name}, {原因}')


if __name__ == '__main__':
    消息队列配置 = config_center.get_rabbitmq(host='ali-hk')
    消费者 = 广播消费者类(
        配置=消息队列配置,
        virtual_host='Crypto',
        exchange_name='crypto.fanout.demo',
        消息回调=消息回调处理,
        连接成功回调=连接成功回调处理,
        连接断开回调=连接断开回调处理
    )
    try:
        result = 消费者.连接()
        if result.is_err():
            raise SystemExit(-1)

        threading.Event().wait()  # 阻塞主线程
    finally:
        消费者.断开()
