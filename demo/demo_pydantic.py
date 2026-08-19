# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-19 11:53:05'

import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, AwareDatetime, field_validator, ValidationError


class Payload2(BaseModel):
    name: str = Field(alias='name', default='')


class ApiResponse(BaseModel):
    # 属性名与JSON键名完全不同
    status_code: int = Field(alias='status', default=-1)
    message_text: str = Field(alias='msg', default='aa')
    data_content: dict = Field(alias='payload', default_factory=dict)
    data_content2: list[Payload2] = Field(alias='payload2', default_factory=list)
    timestamp_value: Optional[AwareDatetime] = Field(alias='time', default=None)  # 字典中的数据必须带带时区信息

    # 数据中是时区0的时间，而我希望是北京时间，所以这里需要指定字段名做转换
    @field_validator('timestamp_value')
    @classmethod
    def convert_to_beijing(cls, v: datetime.datetime) -> datetime.datetime:
        """将时间转换为北京时间"""
        beijing_tz = ZoneInfo('Asia/Shanghai')

        # 如果输入是字符串，先转换为datetime对象
        if isinstance(v, str):
            v = datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))

        # 如果没有时区信息，假设是UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=ZoneInfo('UTC'))

        # 转换为北京时间
        return v.astimezone(beijing_tz)


if __name__ == '__main__':
    # API返回的JSON
    api_response = {
        'status': '200',
        'msg': 'Success',
        'payload': {'user': 'Alice'},
        'payload2': [{'name': '张三'}, {'name': '李四'}],
        'time': '2024-01-01T12:00:00Z'
    }

    try:
        response = ApiResponse(**api_response)
        print(response.status_code)  # 200
        print(response.message_text)  # Success
        print(response.data_content)  # {'user': 'Alice'}
        print(response.data_content2)
        print(response.timestamp_value)  # 2024-01-01T12:00:00Z
    except ValidationError as e:
        print(e)
