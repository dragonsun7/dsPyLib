# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-01-30 15:33:30'

import functools
import logging
import threading

from playhouse.pool import PooledPostgresqlDatabase

"""
    peewee 连接池踩坑日记: http://www.codersec.net/2018/07/peewee%E8%B8%A9%E5%9D%91%E6%97%A5%E8%AE%B0/

    动态定义数据库： https://blog.csdn.net/yangheng816/article/details/61916850


    db = None
    database_proxy = Proxy()

    def initialize(db_name, db_host, db_port, db_usr, db_pwd):
        global db
        db = PooledPostgresqlDatabase(db_name, **{'host': db_host, 'port': db_port, 'user': db_usr, 'password': db_pwd})
        # db = PostgresqlDatabase(db_name, **{'host': db_host, 'port': db_port, 'user': db_usr, 'password': db_pwd})
        database_proxy.initialize(db)
        return db

"""


class DBMgr(object):
    conf = {}
    __instance_lock = threading.Lock()
    __database = None

    @classmethod
    def get_database(cls, refresh=False):
        """
        单例多线程模式获取db对象
        :param refresh: 当为 True 时，强制重建数据库连接池（即使已存在），用于配置变更后刷新连接。
        :return:
        """
        with cls.__instance_lock:
            if (cls.__database is None) or refresh:  # 在无数据库连接池或者要求强制重建数据库连接池时，重建连接池

                # 在有数据库连接池，且要求重建连接池的情况下，先关闭已有的数据库连接池
                if refresh and cls.__database is not None:
                    try:
                        cls.__database.close_all()
                    except Exception as e:
                        logging.error(e)
                    cls.__database = None

                try:
                    db_host = cls.conf['host']
                    db_port = cls.conf['port']
                    db_username = cls.conf['username']
                    db_password = cls.conf['password']
                    db_name = cls.conf["database"]
                    db_max_conn = cls.conf['max_connections']
                    db_stale_timeout = cls.conf['stale_timeout']
                except KeyError:
                    raise Exception('使用前，需要调用init_db()传入数据库配置信息！')

                # DBManager.__database = PostgresqlDatabase(
                #     db_name,
                #     **{
                #         'host': db_host,
                #         'port': db_port,
                #         'user': db_username,
                #         'password': db_password
                #     }
                # )

                # 创建连接池
                cls.__database = PooledPostgresqlDatabase(
                    database=db_name,
                    max_connections=db_max_conn,
                    stale_timeout=db_stale_timeout,
                    **{'host': db_host, 'port': db_port, 'user': db_username, 'password': db_password}
                )
        return cls.__database

    @staticmethod
    def close_database(func):
        """
        装饰器：自动连接数据库，并确保在函数执行完成后关闭数据库连接
        :param func:
        :return:


            from src.pkg.dsQT.db.db_manager import DBManager

            @DBManager.close_database
            def 使用了数据库的方法
        """

        # 加 functools.wraps(func) 保留原函数元信息 (防止装饰后函数的 __name__/__doc__ 丢失)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            db = DBMgr.get_database()
            # # 从连接池取出一个连接，分配给当前线程
            # peewee 的设计里，你不需要显式持有连接对象。连接池在 connect() 后会把连接绑定到当前线程，之后直接用 Model 操作即可
            db.connect(reuse_if_open=True)
            try:
                return func(*args, **kwargs)
            finally:
                db.close()  # 将当前线程的连接归还给连接池（不是真正关闭）

        return wrapper


def init_db(conf: dict):
    """
    使用DBMgr之前必须调用本函数，将数据库配置传递进来
    必须在引入模型之前调用，例如：
        from etc.db import db as db_conf
        from db_mgr import init_db, DBMgr

        if __name__ == '__main__':
            init_db(db_conf)
            from db_bar_daily import DBDailyBar

    @param conf:
        数据库的配置信息，例如：
            {
                'host': '47.75.175.228',
                'port': 5432,
                'username': 'postgres',
                'password': '123456',
                'database': 'vcoin',
                'max_connections': 200,
                'stale_timeout': 30
            }
    """
    DBMgr.conf = conf
