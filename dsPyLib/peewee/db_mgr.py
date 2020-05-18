# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-01-30 15:33:30'

import threading
import logging
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


def init_db(conf: dict):
    """
    使用DBMgr之前必须调用本函数，将数据库配置传递进来
    必须在引入模型之前调用，例如：
        from etc.db import db as db_conf
        from db_mgr import init_db, DBMgr

        if __name__ == '__main__':
            init_db(db_conf)
            from db_bar_daily import DBDailyBar

    :param conf:
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


class DBMgr(object):
    conf = {}
    __instance_lock = threading.Lock()
    __database = None

    @classmethod
    def get_database(cls, refresh=False):
        """
        单例多线程模式获取db对象
        :param refresh:
        :return:
        """
        with DBMgr.__instance_lock:
            if (DBMgr.__database is None) or refresh:
                try:
                    db_host = DBMgr.conf['host']
                    db_port = DBMgr.conf['port']
                    db_username = DBMgr.conf['username']
                    db_password = DBMgr.conf['password']
                    db_name = DBMgr.conf["database"]
                    db_max_conn = DBMgr.conf['max_connections']
                    db_stale_timeout = DBMgr.conf['stale_timeout']
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

                # 连接池
                DBMgr.__database = PooledPostgresqlDatabase(
                    database=db_name,
                    max_connections=db_max_conn,
                    stale_timeout=db_stale_timeout,
                    **{'host': db_host, 'port': db_port, 'user': db_username, 'password': db_password}
                )

            return DBMgr.__database

    @classmethod
    def close_database(cls, func):
        """关闭连接
        :param cls:
        :param func:
        :return:


            from src.pkg.dsQT.db.db_manager import DBManager

            @DBManager.close_database
            def 使用了数据库的方法
        """

        def wrapper(*args, **kwargs):
            try:
                DBMgr.get_database().connect()
            except Exception as e:
                logging.error(e)
            finally:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(e)
                finally:
                    DBMgr.get_database().close()

        return wrapper
