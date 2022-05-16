# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-18 01:15:37'

import datetime

from peewee import Model, DateTimeField, CharField

from dsPyLib.peewee.db_mgr import DBMgr


class DBBaseModel(Model):
    """ 所有模型的基类 """

    class Meta:
        # database = database_proxy
        database = DBMgr.get_database()


class DBStandardModel(DBBaseModel):
    created = DateTimeField(default=datetime.datetime.now, formats='%Y-%m-%d %H:%M:%S.%f', help_text='创建时间')
    updated = DateTimeField(default=datetime.datetime.now, formats='%Y-%m-%d %H:%M:%S.%f', help_text='更新时间')
    remark = CharField(default='', max_length=512, help_text='备注')
