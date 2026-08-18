# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-12-30 15:31:07'

import base64
import hashlib
import hmac
import time
import uuid
from typing import Tuple, OrderedDict
from urllib import parse

import requests
from requests import Response

from dsPyLib.类型.rust_style_result import Result, Ok, Err

"""
    获取Ali服务需要的access_token
    
    文档：
        https://help.aliyun.com/document_detail/72153.html?spm=a2c4g.11186623.2.32.5d375275hoibnU#h2-token-1
        https://help.aliyun.com/document_detail/113251.html?spm=a2c4g.11186623.2.16.3f977229WWmhGp
"""


class AccessToken:

    @staticmethod
    def create_token(access_key_id: str, access_key_secret: str) -> Result[Tuple[str, int], Response]:
        parameters = {'AccessKeyId': access_key_id,
                      'Action': 'CreateToken',
                      'Format': 'JSON',
                      'RegionId': 'cn-shanghai',
                      'SignatureMethod': 'HMAC-SHA1',
                      'SignatureNonce': str(uuid.uuid1()),
                      'SignatureVersion': '1.0',
                      'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      'Version': '2019-02-28'}
        # 构造规范化的请求字符串
        query_string = AccessToken._encode_dict(parameters)
        # print('规范化的请求字符串: %s' % query_string)
        # 构造待签名字符串
        string_to_sign = 'GET' + '&' + AccessToken._encode_text('/') + '&' + AccessToken._encode_text(query_string)
        # print('待签名的字符串: %s' % string_to_sign)
        # 计算签名
        secreted_string = hmac.new(bytes(access_key_secret + '&', encoding='utf-8'),
                                   bytes(string_to_sign, encoding='utf-8'),
                                   hashlib.sha1).digest()
        signature = base64.b64encode(secreted_string)  # bytes
        # print('签名: %s' % signature)
        # 进行URL编码(输出为 str)
        signature_str = AccessToken._encode_text(signature)
        # print('URL编码后的签名: %s' % signature_str)
        # 调用服务(必须用 HTTPS, 请求中包含 AccessKeyId 与签名, 明文传输有泄露风险)
        full_url = 'https://nls-meta.cn-shanghai.aliyuncs.com/?Signature=%s&%s' % (signature_str, query_string)
        # print('url: %s' % full_url)
        # 提交HTTP GET请求(带超时, 防止服务挂起时调用方无限等待)
        response = requests.get(full_url, timeout=10)
        if response.ok:
            try:
                root_obj = response.json()  # 响应可能不是 JSON
            except ValueError:
                return Err(response)
            key = 'Token'
            if key in root_obj:
                token = root_obj[key]['Id']
                expire_time = root_obj[key]['ExpireTime']
                return Ok((token, expire_time))
        return Err(response)

    @staticmethod
    def _encode_text(text) -> str:
        # 兼容 bytes 输入(base64 签名等), 统一转 str 后再编码
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        encoded_text = parse.quote_plus(text)
        return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')

    @staticmethod
    def _encode_dict(dic) -> str:
        dic_sorted = OrderedDict(sorted(dic.items(), key=lambda x: x[0]))
        encoded_text = parse.urlencode(dic_sorted)
        return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')
