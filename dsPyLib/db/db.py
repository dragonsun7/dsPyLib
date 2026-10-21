# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-01-30 15:33:30'

import threading
from typing import Optional, Protocol

from peewee import Proxy
from playhouse.pool import PooledPostgresqlDatabase

from dsPyLib.类型.ds_rust_style_result import Result, Ok, Err

"""
    数据库连接池
    数据库连接池单例
    模型动态代理
    线程安全
    
    使用范式：
        
        1. 初始化
            在应用启动时初始化(调用一次，调用多次只会反复初始化)
            在这个过程中会创建连接池，并为模型挂载代理
            init_db(DBConf(
                host='127.0.0.1', port=5432,
                username='postgres', password='xxx', database='mydb',
                max_connections=20,   # 按并发峰值设
                stale_timeout=300,    # 空闲回收秒数
            ))
            
        2. 查询
            使用with块，在进入块时连接，退出块时关闭连接，保证退出必归还，哪怕块中触发异常
            连接归还的时机是退出with块时，而不是退出函数时
            连接与当前线程关联——不要把 with 块内取得的连接/模型结果跨线程传递使用；
            优雅且安全
            
            db = get_database()
            with db.connection_context():
                return DBStandardModel.select().where(DBStandardModel.id == 用户id).first()
                
            嵌套块安全
            db = get_database()
            with db.connection_context():        # 外层 A: 连接, 栈=[A]
                查询1()
                with db.connection_context():    # 内层 B: 已连接不再连, 栈=[A,B]
                    查询2()
                # 内层 B 退出: 栈=[A] → 不归还
                查询3()       # ← 关键: 必须缩进在外层 A 的 with 块内, 连接才还在
            # 外层 A 退出: 栈=[] → 归还连接            
                
        3. 事务
            db = get_database()
            with db.connection_context():
                with db.atomic():          # 事务: 出错自动回滚
                    for data in datas:
                        DBStandardModel.create(**data)        

    w_peewee 连接池踩坑日记: https://www.codersec.net/2018/07/peewee%E8%B8%A9%E5%9D%91%E6%97%A5%E8%AE%B0/
    动态定义数据库(Proxy 懒加载): https://blog.csdn.net/yangheng816/article/details/61916850
    
    ##############################################
    
    在PyCharm中from playhouse.pool出现红色波浪线
        原因1：
            PyCharm 自带 typeshed 的 peewee 存根，里面内容不完整，没有使用site_packages中的存根
            /Applications/PyCharm.app/Contents/plugins/python-ce/helpers/typeshed/stubs/peewee
            
            解决：
                删除，这样可以禁用PyCharm自带的peewee存根
                "/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/typeshed/stubs/peewee"
        
            说明：
                该 stub 是 partial 的（typeshed 官方自己都标注"不提供所有 playhouse 模块存根"），禁用后用源码解析更准确；
                影响范围：PyCharm 全局（所有项目）——但其他用 peewee 的项目同样受益（源码解析更完整）。
            
        原因2：
            也可能是  PyCharm 的 python_stubs 缓存里有
            PyCharm 会为解释器环境生成一份 python_stubs 缓存（它解析 playhouse 时优先用这份旧缓存)
            查看
                ls ~/Library/Caches/JetBrains/PyCharm2024.3/python_stubs/*/playhouse/

            解决：            
                完全退出PyCharm
                删除
                    rm -rf ~/Library/Caches/JetBrains/PyCharm2024.3/python_stubs
"""

# 用于模型绑定的动态代理，在 import 模型时不用创建连接池，在 init_db() 后代理指向真实的连接池
database_proxy = Proxy()


# 数据库连接池配置
class DBConf(Protocol):
    host: str
    port: int
    username: str
    password: str
    database: str
    max_connections: int  # 例如： 50
    stale_timeout: int  # 例如： 30


# 内部使用的公共变量
_database: Optional[PooledPostgresqlDatabase] = None  # 数据库连接池
_lock = threading.Lock()  # 线程锁


def init_db(conf: DBConf) -> Result[None, Exception]:
    """
    设置配置并重建连接池(幂等: 重复调用自动关闭旧池并重新挂载代理)
    :param conf: 数据库连接池配置(见 DBConf)
    """
    global _database
    with _lock:
        if _database is not None:
            try:
                _database.close_all()
            except Exception as e:
                return Err(e)  # 此时 _database仍然指向旧池

        _database = PooledPostgresqlDatabase(
            host=conf.host,
            port=conf.port,
            user=conf.username,
            password=conf.password,
            database=conf.database,
            max_connections=conf.max_connections,
            stale_timeout=conf.stale_timeout,
        )
        database_proxy.initialize(_database)
        return Ok(None)


def get_database() -> PooledPostgresqlDatabase:
    """
    获取数据库连接池(懒加载: 未 init_db 时抛出清晰错误)
    (单例，有锁，线程安全)
    :return: 连接池对象
    """
    with _lock:
        if _database is None:
            raise RuntimeError('使用前请先调用 init_db()')
        return _database
