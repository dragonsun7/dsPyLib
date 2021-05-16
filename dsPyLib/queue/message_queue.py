# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-06-05 15:11:57'

import json

import pika

# RabbitMQ 保留的队列名(RPC Server)，用于直接回复(Direct reply-to)
# https://pika.readthedocs.io/en/stable/examples/direct_reply_to.html
RESERVED_REPLY_TO_QUEUE = 'amq.rabbitmq.reply-to'

g_username = str()  # RabbitMQ 服务器的用户名
g_password = str()  # RabbitMQ 服务器的密码
g_host = str()  # RabbitMQ 服务器的主机地址
g_port = int()  # RabbitMQ 服务器的主机端口
g_virtual_host = str()


# 外接传递RabbitMQ所需要的参数
def init_mq(username: str, password: str, host: str, port: int, virtual_host: str):
    global g_username
    global g_password
    global g_host
    global g_port
    global g_virtual_host
    g_username = username
    g_password = password
    g_host = host
    g_port = port
    g_virtual_host = virtual_host


# 创建消息队列连接
def create_mq_connection() -> pika.connection:
    credentials = pika.PlainCredentials(username=g_username, password=g_password)
    parameters = pika.ConnectionParameters(host=g_host, port=g_port, virtual_host=g_virtual_host,
                                           credentials=credentials, heartbeat=0)
    connection = pika.BlockingConnection(parameters)
    return connection


def start_direct_reply_to_server(queue: str, consume_proc):
    """
    启动一个直接回复(Direct reply-to)的消息队列服务器(消费者)，启动后会一直阻塞运行

    https://www.rabbitmq.com/direct-reply-to.html
    https://pika.readthedocs.io/en/stable/examples/direct_reply_to.html

    :param queue: 消息队列名
    :param consume_proc: 消费处理函数，原型：def (params: dict) -> dict:
        返回值为：
            {
                'success': True,  # 函数是否执行成功
                'data': data      # 返回的数据
            }
    """

    # 接收到消息后的处理
    def on_server_rx_rpc_request(ch, method_frame, properties, body):
        s = str(body, encoding="utf-8")
        params = json.loads(s)
        data = consume_proc(params)
        ch.basic_publish('', routing_key=properties.reply_to, body=json.dumps(data))
        ch.basic_ack(delivery_tag=method_frame.delivery_tag)

    connection = create_mq_connection()
    channel = connection.channel()

    # Set up server
    channel.queue_declare(queue=queue, exclusive=True, auto_delete=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=on_server_rx_rpc_request)
    channel.start_consuming()


def start_direct_reply_to_client(queue: str, params: dict) -> dict:
    """
    启动一个直接回复(Direct reply-to)的消息队列客户端(发布者)，启动后会一直阻塞运行，直到结果返回

    https://www.rabbitmq.com/direct-reply-to.html
    https://pika.readthedocs.io/en/stable/examples/direct_reply_to.html

    :param queue: 消息队列名
    :param params: 服务端(消费者)需要的参数
    :return: dict, 返回的数据，格式如下：
        {
            'success': True,  # 是否成功消费
            'data': data  # 消费返回的数据
        }
    """
    ret = {}

    connection = create_mq_connection()
    channel = connection.channel()

    # 收到回复后的处理回调函数
    # noinspection PyUnusedLocal
    def on_client_rx_reply_from_server(ch, method_frame, properties, body):
        nonlocal ret
        s = str(body, encoding="utf-8")
        ret = json.loads(s)
        ch.close()

    # Set up client

    # NOTE Client must create its consumer and publish RPC requests on the
    # same channel to enable the RabbitMQ broker to make the necessary
    # associations.
    #
    # Also, client must create the consumer *before* starting to publish the
    # RPC requests.
    #
    # Client must create its consumer with auto_ack=True, because the reply-to
    # queue isn't real.

    channel.basic_consume(queue=RESERVED_REPLY_TO_QUEUE, on_message_callback=on_client_rx_reply_from_server,
                          auto_ack=True)
    channel.basic_publish(exchange='', routing_key=queue, body=str.encode(json.dumps(params), encoding='utf-8'),
                          properties=pika.BasicProperties(reply_to=RESERVED_REPLY_TO_QUEUE))
    channel.start_consuming()
    return ret


def start_subscribe(publish_exchange: str, consume_proc):
    """
    开始订阅(会一直阻塞运行)
    :param publish_exchange: 要订阅的发布交换机名
    :param consume_proc: 消费处理函数，原型：def (params: dict):，不管消费成功还是失败都丢弃
    """

    # noinspection PyUnusedLocal
    def on_message_callback(ch, method, properties, body):
        s = str(body, encoding="utf-8")
        params = json.loads(s)
        consume_proc(params)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    connection = create_mq_connection()  # 创建链接
    channel = connection.channel()  # 获取频道

    # 订阅
    queue = channel.queue_declare('', exclusive=True)  # 创建临时队列(队列名传空字符)，consumer关闭后，队列自动删除
    channel.exchange_declare(exchange=publish_exchange, exchange_type='fanout', durable=False)  # 声明要订阅的发布交换机
    channel.queue_bind(exchange=publish_exchange, queue=queue.method.queue)  # 将临时队列绑定到要订阅的交换机
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue.method.queue, on_message_callback=on_message_callback, auto_ack=False)
    channel.start_consuming()


def publish(publish_exchange: str, data: dict):
    """
    发布消息
    :param publish_exchange: 要发布到的交换机名
    :param data: 消息携带的数据
    """
    connection = create_mq_connection()  # 创建链接
    channel = connection.channel()  # 获取频道
    channel.exchange_declare(exchange=publish_exchange, exchange_type='fanout', durable=False)  # 声明发布交换机
    # delivery_mode = 2 声明消息在队列中持久化，delivery_mod = 1 消息非持久化
    body = str.encode(json.dumps(data), encoding='utf-8')
    channel.basic_publish(exchange=publish_exchange, routing_key='', body=body,
                          properties=pika.BasicProperties(delivery_mode=1))
    connection.close()
