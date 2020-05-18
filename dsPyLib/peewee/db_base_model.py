# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-18 01:15:37'

from peewee import *
from dsPyLib.peewee.db_mgr import DBMgr


class DBBaseModel(Model):
    """ 所有模型的基类 """

    class Meta:
        # database = database_proxy
        database = DBMgr.get_database()
