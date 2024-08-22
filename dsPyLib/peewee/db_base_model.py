# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-18 01:15:37'

from peewee import Model, SQL, DateTimeField, CharField

from dsPyLib.peewee.db_mgr import DBMgr


class DBBaseModel(Model):
    """ 所有模型的基类 """

    @classmethod
    def 属性名转属性列表(cls, 属性名列表: list[str]) -> list:
        return [getattr(cls, x) for x in 属性名列表]

    class Meta:
        # database = database_proxy
        database = DBMgr.get_database()


class DBStandardModel(DBBaseModel):
    created = DateTimeField(formats='%Y-%m-%d %H:%M:%S.%f', constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')],
                            help_text='创建时间')
    updated = DateTimeField(formats='%Y-%m-%d %H:%M:%S.%f', constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')],
                            help_text='更新时间')
    remark = CharField(default='', max_length=512, help_text='备注')
