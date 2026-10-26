# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-10-26 17:28:06'

import threading
from typing import Any

from dsConfigCenter import config_center

from dsPyLib.mqueue.mq_fanout import 广播消费者类
from dsPyLib.utils.logging import logger


def 消息处理(desc: str, data: Any) -> None:
    print(f'{desc}: {data}')


if __name__ == '__main__':
    消息队列配置 = config_center.get_rabbitmq(host='ali-hk')
    消费者 = 广播消费者类(配置=消息队列配置, virtual_host='Crypto', exchange_name='crypto.fanout.demo', 消息处理回调=消息处理)
    try:
        result = 消费者.连接()
        if result.is_err():
            e = result.unwrap_err()
            logger.error(f'消费者连接错误：{e}')
            raise SystemExit(-1)
        threading.Event().wait()
    finally:
        消费者.断开()
