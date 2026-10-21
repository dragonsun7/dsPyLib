# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-05-18 01:15:37'

from peewee import Model, SQL, CharField
from playhouse.postgres_ext import DateTimeTZField

from dsPyLib.db.db import database_proxy


class DBBaseModel(Model):
    """ 所有模型的基类 """

    @classmethod
    def 属性名转属性列表(cls, 属性名列表: list[str]) -> list:
        return [getattr(cls, x) for x in 属性名列表]

    class Meta:
        database = database_proxy  # 懒加载: import 时不创建连接池, init_db() 后代理指向真实连接池


class DBStandardModel(DBBaseModel):
    # peewee 4.x: formats 需为 list(传入 str 会导致 format_date_time 逐字符遍历, 解析失败)
    created = DateTimeTZField(formats=['%Y-%m-%d %H:%M:%S.%f'], constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')],
                              help_text='创建时间')
    updated = DateTimeTZField(formats=['%Y-%m-%d %H:%M:%S.%f'], constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')],
                              help_text='更新时间')
    remark = CharField(default='', max_length=512, help_text='备注')
