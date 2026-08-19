# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-12-30 15:31:07'

"""
    获取Ali服务需要的access_token

    文档：
        https://help.aliyun.com/document_detail/72153.html?spm=a2c4g.11186623.2.32.5d375275hoibnU#h2-token-1
        https://help.aliyun.com/document_detail/113251.html?spm=a2c4g.11186623.2.16.3f977229WWmhGp
"""

import base64
import hashlib
import hmac
import threading
import time
import uuid
from collections import OrderedDict
from typing import Union, Optional
from urllib import parse

from pydantic import BaseModel, Field

from dsPyLib.utils.ds_request import ds_get, response_data_to_dict
from dsPyLib.类型.ds_dict import get_dict_value, dict_to_model
from dsPyLib.类型.ds_rust_style_result import Result, Ok, Err


class TokenModel(BaseModel):
    user_id: str = Field(alias='UserId', default='')
    token: str = Field(alias='Id', default='')
    expire_time: int = Field(alias='ExpireTime', default=0)

    def 已过期(self) -> bool:
        return (self.expire_time > 0) and (int(time.time()) >= self.expire_time)


class AccessToken:

    def __init__(self, access_key_id: str, access_key_secret: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

        self._token_model: Optional[TokenModel] = None
        self._lock = threading.Lock()  # 线程安全: 同实例并发调用只发一次请求(单飞)

    def token(self) -> Result[str, Exception]:
        """
        获取 access token(带实例级缓存, 未获取或已过期时自动重新请求)

        功能: 首次调用请求阿里云并缓存; 有效期内直接返回缓存
        用法:
            client = AccessToken(access_key_id, access_key_secret)
            result = client.token()
            if result.is_ok():
                token = result.ok_value()
        """
        with self._lock:
            未获取 = self._token_model is None
            已过期 = self._token_model and self._token_model.已过期()
            if 未获取 or 已过期:
                result = self.create_token(access_key_id=self.access_key_id, access_key_secret=self.access_key_secret)
                if result.is_err():
                    return Err(result.unwrap_err())
                self._token_model = result.unwrap()
            assert self._token_model is not None  # 收窄: 缓存有效或刚获取, 必非空(给类型查看器看的)
            return Ok(self._token_model.token)

    @staticmethod
    def create_token(access_key_id: str, access_key_secret: str) -> Result[TokenModel, Exception]:
        # 生成请求参数列表
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
        # 构造待签名字符串
        string_to_sign = 'GET' + '&' + AccessToken._encode_text('/') + '&' + AccessToken._encode_text(query_string)
        # 计算签名
        secreted_string = hmac.new(bytes(access_key_secret + '&', encoding='utf-8'),
                                   bytes(string_to_sign, encoding='utf-8'),
                                   hashlib.sha1).digest()
        # 进行URL编码(输出为 str)
        signature = base64.b64encode(secreted_string)  # bytes
        signature_str = AccessToken._encode_text(signature)
        # 生成URL(必须用 HTTPS, 请求中包含 AccessKeyId 与签名, 明文传输有泄露风险)
        full_url = 'https://nls-meta.cn-shanghai.aliyuncs.com/?Signature=%s&%s' % (signature_str, query_string)

        # 发起网络请求
        result1 = ds_get(full_url)
        if result1.is_err():
            return Err(result1.unwrap_err())
        response = result1.unwrap()

        # 拆解出响应字典
        result2 = response_data_to_dict(response)
        if result2.is_err():
            return Err(result2.unwrap_err())
        root_dict = result2.unwrap()

        # 拆解出Token字典
        result3 = get_dict_value(data=root_dict, keypath='Token', expected_type=dict)
        if result3.is_err():
            return Err(result3.unwrap_err())
        token_dict = result3.unwrap()

        # 生成模型
        result4 = dict_to_model(data=token_dict, model_class=TokenModel)
        if result4.is_err():
            return Err(result4.unwrap_err())
        model = result4.unwrap()

        return Ok(model)

    @staticmethod
    def _encode_text(text: Union[str, bytes]) -> str:
        s = text.decode('utf-8') if isinstance(text, bytes) else text  # 兼容 bytes 输入(base64 签名等), 统一转 str 后再编码
        encoded_text = parse.quote_plus(s)
        return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')

    @staticmethod
    def _encode_dict(dic: dict) -> str:
        dic_sorted = OrderedDict(sorted(dic.items(), key=lambda x: x[0]))
        encoded_text = parse.urlencode(dic_sorted)
        return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')
