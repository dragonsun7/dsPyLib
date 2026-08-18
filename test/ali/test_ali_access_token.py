# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-17 17:30:00'

"""
    dsPyLib/ali/ali_access_token.py 的单元测试
    阿里云凭据从 dsConfigCenter 获取
"""

import unittest
from unittest import mock

from dsConfigCenter import config_center
from requests import Response
from requests.exceptions import ContentDecodingError

from dsPyLib.ali.ali_access_token import AccessToken


class TestCreateToken(unittest.TestCase):

    def test_生成真实Token(self):
        ali = config_center.get_ali()
        result = AccessToken.create_token(access_key_id=ali.access_key_id, access_key_secret=ali.access_key_secret)
        if result.is_ok():
            assert result.ok_value() is not None  # 类型收窄: 成功时必有值
            token, expire_time = result.ok_value()
            print(token, expire_time)
            self.assertIsInstance(token, str)
            self.assertIsInstance(expire_time, int)
        else:
            print(f'请求失败：{result.err_value()}')
            self.assertIsInstance(result.err_value(), Response)


class 测试_encode_text(unittest.TestCase):
    """_encode_text 的 RFC3986 编码规则"""

    def test_普通字符不变(self):
        self.assertEqual(AccessToken._encode_text('abc123'), 'abc123')

    def test_空格编码(self):
        self.assertEqual(AccessToken._encode_text('a b'), 'a%20b')

    def test_星号编码(self):
        self.assertEqual(AccessToken._encode_text('a*b'), 'a%2Ab')

    def test_波浪号保留(self):
        self.assertEqual(AccessToken._encode_text('a~b'), 'a~b')

    def test_斜杠编码(self):
        self.assertEqual(AccessToken._encode_text('a/b'), 'a%2Fb')

    def test_中文编码(self):
        self.assertEqual(AccessToken._encode_text('中文'), '%E4%B8%AD%E6%96%87')

    def test_字节输入返回字符串(self):
        result = AccessToken._encode_text(b'AbC+dEf=gH==')
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'AbC%2BdEf%3DgH%3D%3D')


class 测试_encode_dict(unittest.TestCase):
    """_encode_dict 的 RFC3986 编码规则(键排序 + 值编码)"""

    def test_字典按键名排序(self):
        result = AccessToken._encode_dict({'b': 2, 'a': 1, 'c': 3})
        self.assertEqual(result, 'a=1&b=2&c=3')

    def test_字典值编码(self):
        result = AccessToken._encode_dict({'a': 'x y', 'c': '中文'})
        self.assertEqual(result, 'a=x%20y&c=%E4%B8%AD%E6%96%87')


class 测试create_token分支(unittest.TestCase):
    """create_token 的分支覆盖(网络已 mock, 不依赖真实请求)"""

    @staticmethod
    def _构造响应(ok=True, json_data=None, 抛异常=None):
        响应 = mock.Mock()
        响应.ok = ok
        if 抛异常:
            响应.json.side_effect = 抛异常
        else:
            响应.json.return_value = json_data
        return 响应

    @mock.patch('dsPyLib.ali.ali_access_token.requests.get')
    def test_请求失败返回Err(self, mock_get):
        响应 = self._构造响应(ok=False)
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self.assertTrue(result.is_err())
        self.assertIs(result.err_value(), 响应)  # 返回的就是同一个响应对象

    @mock.patch('dsPyLib.ali.ali_access_token.requests.get')
    def test_响应非JSON返回Err(self, mock_get):
        响应 = self._构造响应(ok=True, 抛异常=ValueError('非JSON内容'))
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self.assertTrue(result.is_err())
        self.assertIs(result.err_value(), 响应)  # 返回的就是同一个响应对象

    @mock.patch('dsPyLib.ali.ali_access_token.requests.get')
    def test_响应内容解码异常返回Err(self, mock_get):
        # 覆盖 ContentDecodingError(非 ValueError 子类, 需单独捕获)
        响应 = self._构造响应(ok=True, 抛异常=ContentDecodingError('解码失败'))
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self.assertTrue(result.is_err())
        self.assertIs(result.err_value(), 响应)  # 返回的就是同一个响应对象

    @mock.patch('dsPyLib.ali.ali_access_token.requests.get')
    def test_JSON缺少Token键返回Err(self, mock_get):
        响应 = self._构造响应(ok=True, json_data={'Other': 1})
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self.assertTrue(result.is_err())
        self.assertIs(result.err_value(), 响应)  # 返回的就是同一个响应对象

    @mock.patch('dsPyLib.ali.ali_access_token.requests.get')
    def test_成功返回Ok(self, mock_get):
        mock_get.return_value = self._构造响应(ok=True, json_data={'Token': {'Id': 'TOKEN123', 'ExpireTime': 1234567890}})
        result = AccessToken.create_token('AK', 'SK')
        self.assertTrue(result.is_ok())
        assert result.ok_value() is not None  # 类型收窄
        token, expire_time = result.ok_value()
        self.assertEqual(token, 'TOKEN123')
        self.assertEqual(expire_time, 1234567890)

    @mock.patch('dsPyLib.ali.ali_access_token.requests.get')
    def test_请求URL包含必需参数(self, mock_get):
        mock_get.return_value = self._构造响应(ok=True, json_data={'Token': {'Id': 'T', 'ExpireTime': 1}})
        AccessToken.create_token('AK_ID', 'AK_SECRET')
        url = mock_get.call_args[0][0]
        self.assertIn('https://nls-meta.cn-shanghai.aliyuncs.com/', url)
        self.assertIn('Signature=', url)
        self.assertIn('AccessKeyId=AK_ID', url)
        self.assertIn('Action=CreateToken', url)
        self.assertIn('SignatureMethod=HMAC-SHA1', url)
        self.assertIn('SignatureVersion=1.0', url)
        self.assertIn('Version=2019-02-28', url)
        self.assertIn('RegionId=cn-shanghai', url)

    @mock.patch('dsPyLib.ali.ali_access_token.requests.get')
    def test_请求带超时(self, mock_get):
        mock_get.return_value = self._构造响应(ok=True, json_data={'Token': {'Id': 'T', 'ExpireTime': 1}})
        AccessToken.create_token('AK', 'SK')
        self.assertEqual(mock_get.call_args[1]['timeout'], 10)


if __name__ == '__main__':
    unittest.main()
