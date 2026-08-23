# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2022-05-16 10:26:48'

"""
    迁移

    流程：
         1. 删除视图
         2. 删除函数
         3. 删除表
         4. 创建表
         5. 创建默认函数
         6. 创建默认触发器
         7. 执行其它任务(例如：创建 触发器/函数/视图/，清除/写入初始数据等
        
    用法：
        1. 派生DBMigrate类
        2. 根据情况重写下面的函数：
            def views_for_drop(self) -> list[str]:                      指定要删除的视图名称列表
            def funcs_for_drop(self) -> list[str]:                      指定要删除的函数名称列表
            def tables_for_drop(self) -> list[type[DBStandardModel]]:   指定要删除的表结构模型列表    
            def tables_for_create(self) -> list[type[DBStandardModel]]: 指定要创建的表结构模型列表
            def after(self, db):                                        执行其它任务(例如：创建 触发器/函数/视图/，清除/写入初始数据等)
        3. 调用 execute()
"""

import logging
import os

from dsPyLib.utils.logging import logger
from .db import get_database
from .model import DBStandardModel


# noinspection PyMethodMayBeStatic
class DBMigrate(object):

    def __init__(self, log: bool = True):
        self.db = get_database()
        if log:
            peewee_logger = logging.getLogger('peewee')
            peewee_logger.setLevel(logging.DEBUG)
            # 防止 handler 重复添加，避免每次构造 DBMigrate() 都会 addHandler(StreamHandler()
            # 多次构造日志会重复输出
            if not peewee_logger.handlers:
                peewee_logger.addHandler(logging.StreamHandler())

    def execute(self):
        with self.db.atomic():  # 可回滚
            # 1. 删除视图
            view_names = self.views_for_drop()
            for view_name in view_names:
                self._drop_view(name=view_name)

            # 2. 删除函数
            func_names = self.funcs_for_drop()
            for func_name in func_names:
                self._drop_func(name=func_name)

            # 3. 删除表
            models = self.tables_for_drop()
            self.db.drop_tables(models=models)

            # 4. 创建表
            models = self.tables_for_create()
            self.db.create_tables(models=models)

            # 5. 创建默认函数
            self._create_default_funcs()

            # 6. 创建默认触发器
            self._create_default_triggers(models=models)

            # 7. 执行其它任务(例如：创建 触发器/函数/视图/，清除/写入初始数据等
            self.after(db=self.db)

            logger.info('创建表结构完成！')

    # ---------- 重载 ---------- #

    # 重载：指定要删除的视图名称列表
    def views_for_drop(self) -> list[str]:
        return []

    # 重载：指定要删除的函数名称列表
    def funcs_for_drop(self) -> list[str]:
        return []

    # 重载：指定要删除的表结构模型列表
    def tables_for_drop(self) -> list[type[DBStandardModel]]:
        return []

    # 重载：指定要创建的表结构模型列表
    def tables_for_create(self) -> list[type[DBStandardModel]]:
        return []

    # 重载: 执行其它任务(例如：创建 触发器/函数/视图/，清除/写入初始数据等
    def after(self, db):
        # 清除数据时，引用了外键的要先删除
        pass

    # ---------- 私有 ---------- #

    # 删除视图
    def _drop_view(self, name: str):
        sql = f'DROP VIEW IF EXISTS {name};'
        self.db.execute_sql(sql=sql, params=None)

    # 删除函数
    def _drop_func(self, name: str):
        sql = f'DROP FUNCTION IF EXISTS {name};'
        self.db.execute_sql(sql=sql, params=None)

    # 创建默认函数
    def _create_default_funcs(self):
        # 用于updated字段触发器的函数
        sql_file = os.path.join(os.path.dirname(__file__), 'sql', 'create_func_updated.sql')
        with open(sql_file, 'r', encoding='utf8') as fp:
            sql = fp.read()
            self.db.execute_sql(sql=sql)

    # 创建默认触发器
    def _create_default_triggers(self, models: list[type[DBStandardModel]]):
        # 创建默认的updated字段的触发器
        sql_file = os.path.join(os.path.dirname(__file__), 'sql', 'create_trigger_updated.sql')
        for model_class in models:
            with open(sql_file, 'r', encoding='utf8') as fp:
                table_name = model_class._meta.table_name
                sql = fp.read()
                sql = sql.replace('__table_name__', table_name)
                self.db.execute_sql(sql=sql)
