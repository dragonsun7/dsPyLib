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
from typing import Tuple, Union, Optional
from urllib import parse

import requests

from dsPyLib.类型.rust_style_result import Result, Ok, Err


class AccessToken:

    def __init__(self, access_key_id: str, access_key_secret: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

        self._token: Optional[str] = None
        self._expire_time: Optional[int] = None
        self._lock = threading.Lock()  # 线程安全: 同实例并发调用只发一次请求(单飞)

    def token(self) -> Result[str, str]:
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
            未获取 = not self._token
            已过期 = self._expire_time is not None and (int(time.time()) >= self._expire_time)
            if 未获取 or 已过期:
                result = self.create_token(access_key_id=self.access_key_id, access_key_secret=self.access_key_secret)
                if result.is_err():
                    return Err(result.unwrap_err())
                self._token, self._expire_time = result.unwrap()
            assert self._token is not None  # 收窄: 缓存有效或刚获取, 必非空(给类型查看器看的)
            return Ok(self._token)

    @staticmethod
    def create_token(access_key_id: str, access_key_secret: str) -> Result[Tuple[str, int], str]:
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
        # 调用服务(必须用 HTTPS, 请求中包含 AccessKeyId 与签名, 明文传输有泄露风险)
        full_url = 'https://nls-meta.cn-shanghai.aliyuncs.com/?Signature=%s&%s' % (signature_str, query_string)

        # 发起网络请求
        try:
            response = requests.get(full_url, timeout=10)  # 提交HTTP GET请求(带超时, 防止服务挂起时调用方无限等待)
        except requests.exceptions.RequestException as e:  # 网络层异常(连接失败/超时/DNS等)
            return Err(f'网络请求失败：{str(e)}')

        # 验证响应成功状态
        if not response.ok:
            return Err(f'网络请求响应失败: {response.status_code}, {response.reason}, {response.text}')

        # 拆解响应内容
        try:
            root_obj = response.json()
        except (ValueError, requests.exceptions.RequestException) as e:
            # 覆盖:
            #   JSONDecodeError(ValueError子类)
            #   UnicodeDecodeError(ValueError子类)
            #   ContentDecodingError(内容解码或解压损坏, 属 RequestException)
            return Err(f'解析网络请求响应内容失败：{str(e)}')

        # 提取数据
        if not isinstance(root_obj, dict):
            return Err(f'响应内容不正确：: {root_obj}')
        token_info = root_obj.get('Token')
        if not isinstance(token_info, dict):  # Token 缺失或不是 dict(如字符串/列表), 避免 AttributeError 逃逸
            return Err('未能正确获取 Token_Info！')
        token = token_info.get('Id')
        expire_time = token_info.get('ExpireTime')
        if not isinstance(token, str):
            return Err('未能正确获取 Token！')
        if expire_time is None:
            return Err('未能正确获取 ExpireTime！')
        try:
            expire_timestamp = int(str(expire_time))
        except (ValueError, TypeError):
            return Err(f'未能正确转换ExpireTime:{expire_time}')

        return Ok((token, expire_timestamp))

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
