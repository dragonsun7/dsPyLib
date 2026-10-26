# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-10-26 14:55:27'

"""
    安装包：
        pika.Connection 在1.5.0才开始有，目前只有开发版
        uv pip install git+https://github.com/pika/pika.git
        pip install git+https://github.com/pika/pika.git
        之前用的 SelectConnection 必须由自己调用 ioloop.start() 来驱动，这一调用会阻塞当前线程。
        而 pika.Connection 把这个循环藏到了后台，对外暴露的是阻塞式但线程安全的 API，正好符合“主线程还要干别的”这个需求。

    需求：
        1. 多个生产者发布消息
        2. 可能有0或者多个消费者获取消息，要求所有消费者都收到消息，如果没有消费者则丢弃消息

    方案：
        要实现“所有消费者都收到”，必须利用 Fanout（广播）交换机，并为每个消费者实例分配独立的队列。
            * 交换机类型：Fanout 会将收到的消息复制到所有绑定的队列
            * 每个消费者对应一个独立的队列，这样消费者会收到所有的消息；如果多个消费者绑定一个队列会轮流消费
            * 队列使用临时队列，声明队列时使用exclusive=true 或 auto-delete=true，断开后队列自动删除，不会留下无人消费的“僵尸队列”继续接收并堆积消息。
            * 消费者使用自动确认（autoAck），消费完即删除消息，符合消费后丢弃的要求
            * 无消费者时的消息丢弃，两种 TTL 配合使用
                消息过期	    x-message-ttl	消息在队列中存活的最长时间，超时即丢弃	            
                比如拉取5分钟数据，就设 x-message-ttl=300000（5 分钟），过期的数据没有消费价值

    总结
        生产者：发送消息到 Fanout 交换机（不指定路由键，指定了也会被忽略）。
        消费者启动时：声明一个独占/自动删除的临时队列，绑定到该 Fanout 交换机，然后开始消费。
        消息分发：Fanout 交换机把消息复制到每一个当前存在的绑定队列。每个消费者从自己的队列里拿到一份。
        无消费者时：
            如果没有任何队列绑定（所有消费者都离线），消息到达 Fanout 交换机后直接被丢弃，因为交换机本身不存储消息。
            即使有残留队列但消费者已断开，x-message-ttl 也会让消息过期删除。            
"""

import pickle
import threading
from typing import Optional, Protocol, Callable, TypeAlias, Any

import pika
from pika.adapters.thread_safe_connection import Connection, Channel
from pika.spec import Basic, BasicProperties

from dsPyLib.utils.logging import logger
from dsPyLib.类型.ds_rust_style_result import Result, Ok, Err

消息处理回调类型: TypeAlias = Callable[[str, Any], None]  # 实现形式：def 消息处理(desc: str, data: Any) -> None:


class 消息队列配置信息协议(Protocol):
    host: str
    port: int
    username: str
    password: str


class _基类(object):
    """连接、交换机声明、安全关闭的公共逻辑。"""

    def __init__(self, 配置: 消息队列配置信息协议, virtual_host: str, exchange_name: str):
        self.配置 = 配置
        self.virtual_host = virtual_host
        self.exchange_name = exchange_name

        self._conn: Optional[Connection] = None
        self._channel: Optional[Channel] = None

        self._lock = threading.RLock()  # 线程锁

    # ---------------------------------------- 对外 ---------------------------------------- #

    @property
    def 已连接(self) -> bool:
        return bool(self._conn and self._conn.is_open and self._channel and self._channel.is_open)

    def 连接(self) -> Result[None, Exception]:
        """
        连接整合了三个步骤：
            1. 创建一个链接，并赋给 self_conn
            2. 打开一个新信道，并赋给 self._channel
            3. 声明交换机
        """

        with self._lock:
            try:
                # 先断开旧连接
                self.断开()

                # 准备连接参数
                parameters = pika.ConnectionParameters(
                    host=self.配置.host,
                    port=self.配置.port,
                    virtual_host=self.virtual_host,
                    credentials=pika.PlainCredentials(
                        username=self.配置.username,
                        password=self.配置.password,
                    ),
                    heartbeat=20,  # 20s 心跳，约 40s 可发现断连
                    blocked_connection_timeout=30,  # broker 资源告警时不无限挂起
                    client_properties={
                        'connection_name': f'dsPyLib.mq_fanout.{type(self).__name__}.{self.exchange_name}',  # 便于在 RabbitMQ 管理界面按名称定位连接
                    },
                )

                # Connection 连接建立后，IOLoop 自动在后台线程运行，不阻塞主线程(这是 SelectConnection, BlockingConnection 不具备的)
                self._conn = Connection(parameters=parameters, on_close_callback=self._handle_close_callback)  # 关闭时的回调

                # 打开一个新信道
                self._channel = self._conn.channel()

                # 声明交换机
                self._channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type='fanout',  # 广播
                    durable=True,  # 长久保持
                )

                return Ok(None)
            except Exception as e:
                self.断开()
                return Err(e)

    def 断开(self) -> None:
        """
            先摘掉引用再关闭：
                1. 幂等：重复调用不会再次 close
                2. 状态一致：已连接 立即变 False，close 阻塞期间不会被误判为可用
                3. 异常安全：close 失败也不会留下"半关闭但仍被引用"的对象
                局部变量 channel/conn 负责在置 None 之后仍能完成关闭。

            为什么要加锁？
                close() 本身线程安全，加锁不是为了保护 pika，
                而是保护 self._conn 和 self._channel 的"检查 → 使用/替换"序列。
                比如：需要保证在 “检查连接 → 发布” 期间，没人把 self._conn 和 self._channel 换掉或关掉
        """
        with self._lock:
            channel, conn = self._channel, self._conn
            self._channel = None
            self._conn = None

            for obj, 名称 in ((channel, 'channel'), (conn, 'connection')):
                if obj is None:
                    continue

                try:
                    if obj.is_open:
                        obj.close(timeout=5)
                except Exception as e:
                    logger.warning(f'关闭 {名称} 失败: {e!r}')

    # ---------------------------------------- 私有 ---------------------------------------- #

    def _handle_close_callback(self, connection, reason):
        # 在这里处理断线重连(暂不处理)
        pass


class 广播发布者类(_基类):

    def 发布(self, desc: str, data) -> Result[None, Exception]:
        """
            发送协议：
                将参数组合为字典：{"desc": desc, "data": data}
                然后用pickle转换为字节流传递
        """

        with self._lock:  # 多线程下，“检查 → 发布” 可能在这两步之间，self._channel 被修改，所以需要加锁
            # 检查连接状态
            if not self.已连接:
                return Err(ConnectionError('发布时发现未连接'))

            # 发布消息
            try:
                d = {'desc': desc, 'data': data}
                body: bytes = pickle.dumps(d)

                self._channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key='',
                    body=body,
                    properties=pika.BasicProperties(
                        content_type='application/x-python-pickle',
                        delivery_mode=1,  # 消息实时广播，不要求持久化
                    ),
                )
                return Ok(None)
            except Exception as e:
                return Err(e)


class 广播消费者类(_基类):

    def __init__(self, 配置: 消息队列配置信息协议, virtual_host: str, exchange_name: str, 消息处理回调: 消息处理回调类型):
        super().__init__(配置=配置, virtual_host=virtual_host, exchange_name=exchange_name)

        self.消息处理回调: Optional[消息处理回调类型] = 消息处理回调

    def 连接(self) -> Result[None, Exception]:
        """
        连接后立即进入消费状态
        """
        with self._lock:
            result = super().连接()
            if result.is_err():
                return result

            try:
                # 每个消费者声明一个独立的临时队列
                queue_declare = self._channel.queue_declare(
                    queue='',  # 由于是临时的，交给服务器自动生成队列名
                    exclusive=True,  # 连接断开自动删除(已经保证断连删除，auto_delete()没啥用)
                    arguments={
                        'x-message-ttl': 60000,  # 消息最多保留 1 分钟
                    },
                )

                # 获取队列名
                queue_name = queue_declare.method.queue

                # 将队列绑定到交换机
                self._channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=queue_name,
                    routing_key='',  # fanout 忽略路由键
                )

                # 开始消费
                # def (channel: Channel, method: Basic, properties: BasicProperties, body: bytes) -> None:
                self._channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=self._handle_message_callback,
                    auto_ack=True,  # 消费即丢弃
                )
                return Ok(None)
            except Exception as e:
                self.断开()
                return Err(e)

    # ---------------------------------------- 私有 ---------------------------------------- #

    def _handle_message_callback(self, _: Channel, __: Basic, properties: BasicProperties, body: bytes) -> None:
        """
        将数据用pickle还原，并分别返回 desc 和 data
        """
        if properties.content_type != 'application/x-python-pickle':
            logger.warning(f'忽略未知编码: {properties.content_type!r}')
            return

        try:
            d = pickle.loads(body)
        except Exception as e:
            logger.exception(f'pickle 解码失败：{e}')
            return

        try:
            self.消息处理回调(d['desc'], d['data'])
        except Exception as e:
            logger.exception(f'处理消息错误：{e}')
