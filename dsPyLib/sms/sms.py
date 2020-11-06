# -*- coding: utf-8 -*-
__author__ = 'Dragon Sun'

# 使用云之讯接口发送短信
# http://www.ucpaas.com/


import requests
import uuid
import json

g_sid = '填写你的 sid'
g_token = '填写你的 token'
g_app_id = '填写你的 app_id'


# 设置全局Keys(在使用前必须调用该函数传入相关信息)
def set_sms_keys(sid: str, token: str, app_id: str):
    global g_sid
    global g_token
    global g_app_id
    g_sid = sid
    g_token = token
    g_app_id = app_id


def send_sms(mobile: str, template_id: int, params: list) -> dict:
    """
    发送短信
    :param mobile: 手机号码
    :param template_id: 短信模板ID
    :param params: 参数列表，个数取决于短信模板里设置的参数数量
    :return: 短信平台返回的信息
    """
    url = 'https://open.ucpaas.com/ol/sms/sendsms'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=utf-8'
    }
    params = {
        'sid': g_sid,
        'token': g_token,
        'appid': g_app_id,
        'templateid': template_id,
        'param': ','.join(params),
        'mobile': mobile,
        'uid': str(uuid.uuid4()).replace('-', '')
    }
    response = requests.post(url, json.dumps(params), headers=headers)
    content = str(response.content, encoding='utf-8')
    return json.loads(content)


if __name__ == '__main__':
    print(send_sms('13980660107', 314842, ['OKB_USDT', '拉升']))
