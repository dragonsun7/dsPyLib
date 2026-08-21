# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-17 17:30:00'

"""
    dsPyLib/ali/ali_access_token.py 的单元测试
    阿里云凭据从 dsConfigCenter 获取
"""

import time
import unittest
from unittest import mock

from dsConfigCenter import config_center
from requests.exceptions import ContentDecodingError, ConnectionError, HTTPError, Timeout

from dsPyLib.ali.ali_access_token import AccessToken, TokenModel
from dsPyLib.类型.ds_rust_style_result import Ok, Err, ResultException


class TestCreateToken(unittest.TestCase):

    def test_生成真实Token(self):
        ali = config_center.get_ali()
        result = AccessToken.create_token(access_key_id=ali.access_key_id, access_key_secret=ali.access_key_secret)
        if result.is_ok():
            token = result.unwrap().token
            print(token)
            self.assertIsInstance(token, str)
        else:
            print(f'请求失败：{result.unwrap_err()}')
            self.assertIsInstance(result.unwrap_err(), Exception)

    def test_获取Token(self):
        ali = config_center.get_ali()
        access_token_obj = AccessToken(access_key_id=ali.access_key_id, access_key_secret=ali.access_key_secret)
        result = access_token_obj.token()
        if result.is_ok():
            token = result.unwrap()
            print(token)
            self.assertIsInstance(token, str)
        else:
            print(f'获取Token失败：{result.unwrap_err()}')
            self.assertIsInstance(result.unwrap_err(), Exception)


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

    def _断言错误包含(self, result, 片段):
        # 断言 Result 为 Err 且错误信息包含指定片段(收窄 Optional[str])
        self.assertTrue(result.is_err())
        错误 = result.err_value()
        assert 错误 is not None  # 类型收窄: 失败时必有错误
        self.assertIn(片段, str(错误))

    def _断言是Err(self, result):
        # 断言 Result 为 Err 且错误值为 Exception(新工具链的异常契约)
        self.assertTrue(result.is_err())
        self.assertIsInstance(result.err_value(), Exception)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_请求失败返回Err(self, mock_get):
        # ds_get 用 raise_for_status() 检查状态码, 失败时返回原始 HTTPError(不再返回'响应失败'文案)
        响应 = self._构造响应(ok=False)
        响应.raise_for_status.side_effect = HTTPError('404 Client Error')
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self._断言是Err(result)
        self.assertIn('404', str(result.err_value()))

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_响应非JSON返回Err(self, mock_get):
        响应 = self._构造响应(ok=True, 抛异常=ValueError('非JSON内容'))
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self._断言是Err(result)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_响应内容解码异常返回Err(self, mock_get):
        # 覆盖 ContentDecodingError(非 ValueError 子类, 需单独捕获)
        响应 = self._构造响应(ok=True, 抛异常=ContentDecodingError('解码失败'))
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self._断言是Err(result)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_JSON缺少Token键返回Err(self, mock_get):
        响应 = self._构造响应(ok=True, json_data={'Other': 1})
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self._断言是Err(result)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_成功返回Ok(self, mock_get):
        mock_get.return_value = self._构造响应(ok=True, json_data={'Token': {'Id': 'TOKEN123', 'ExpireTime': 1234567890}})
        result = AccessToken.create_token('AK', 'SK')
        self.assertTrue(result.is_ok())
        assert result.ok_value() is not None  # 类型收窄
        模型 = result.ok_value()
        assert 模型 is not None  # 类型收窄
        self.assertEqual(模型.token, 'TOKEN123')
        self.assertEqual(模型.expire_time, 1234567890)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_请求URL包含必需参数(self, mock_get):
        mock_get.return_value = self._构造响应(ok=True, json_data={'Token': {'Id': 'T', 'ExpireTime': 1}})
        AccessToken.create_token('AK_ID', 'AK_SECRET')
        url = mock_get.call_args.kwargs['url']  # ds_get 用关键字 url= 调用
        self.assertIn('https://nls-meta.cn-shanghai.aliyuncs.com/', url)
        self.assertIn('Signature=', url)
        self.assertIn('AccessKeyId=AK_ID', url)
        self.assertIn('Action=CreateToken', url)
        self.assertIn('SignatureMethod=HMAC-SHA1', url)
        self.assertIn('SignatureVersion=1.0', url)
        self.assertIn('Version=2019-02-28', url)
        self.assertIn('RegionId=cn-shanghai', url)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_连接异常返回Err(self, mock_get):
        # 覆盖网络层异常(连接拒绝), 应归入 Err 而非逃逸
        mock_get.side_effect = ConnectionError('连接被拒绝')
        result = AccessToken.create_token('AK', 'SK')
        self._断言是Err(result)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_超时返回Err(self, mock_get):
        # 覆盖超时异常
        mock_get.side_effect = Timeout('请求超时')
        result = AccessToken.create_token('AK', 'SK')
        self._断言是Err(result)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_Token缺少ExpireTime用默认值(self, mock_get):
        # Token 对象缺少 ExpireTime: TokenModel 有默认值 0, 应返回 Ok(行为与旧版不同)
        响应 = self._构造响应(ok=True, json_data={'Token': {'Id': 'T'}})
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self.assertTrue(result.is_ok())
        模型 = result.ok_value()
        assert 模型 is not None  # 类型收窄
        self.assertEqual(模型.expire_time, 0)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_响应内容非dict返回Err(self, mock_get):
        # 根对象不是 dict(如字符串), 应返回 Err
        响应 = self._构造响应(ok=True, json_data='不是dict')
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self.assertTrue(result.is_err())
        self._断言是Err(result)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_Token非dict返回Err(self, mock_get):
        # Token 字段存在但不是 dict(字符串/列表), 不应抛 AttributeError
        响应 = self._构造响应(ok=True, json_data={'Token': 'not-a-dict'})
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self.assertTrue(result.is_err())
        self._断言是Err(result)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_ExpireTime转换失败返回Err(self, mock_get):
        # ExpireTime 无法转 int(如 'abc'), 应返回 Err 而非抛异常
        响应 = self._构造响应(ok=True, json_data={'Token': {'Id': 'T', 'ExpireTime': 'abc'}})
        mock_get.return_value = 响应
        result = AccessToken.create_token('AK', 'SK')
        self._断言是Err(result)

    @mock.patch('dsPyLib.utils.ds_request.requests.get')
    def test_请求带超时(self, mock_get):
        mock_get.return_value = self._构造响应(ok=True, json_data={'Token': {'Id': 'T', 'ExpireTime': 1}})
        AccessToken.create_token('AK', 'SK')
        self.assertEqual(mock_get.call_args[1]['timeout'], 10)


class 测试令牌缓存(unittest.TestCase):
    """实例级 token 缓存: 未获取/过期时请求, 有效期内命中缓存"""

    @staticmethod
    def _构造模型(token='TOKEN', 过期时间=None):
        # 按别名构造(源码 TokenModel 未开 populate_by_name, 只接受别名键)
        return TokenModel(UserId='', Id=token,
                          ExpireTime=过期时间 if 过期时间 is not None else int(time.time()) + 3600)

    @mock.patch('dsPyLib.ali.ali_access_token.AccessToken.create_token')
    def test_首次请求后命中缓存(self, mock_create):
        mock_create.return_value = Ok(self._构造模型())
        实例 = AccessToken('AK', 'SK')
        result1 = 实例.token()
        result2 = 实例.token()
        self.assertEqual(result1.ok_value(), 'TOKEN')
        self.assertEqual(result2.ok_value(), 'TOKEN')
        self.assertEqual(mock_create.call_count, 1, '第二次应命中缓存, 不重复请求')

    @mock.patch('dsPyLib.ali.ali_access_token.AccessToken.create_token')
    def test_过期后重新请求(self, mock_create):
        mock_create.return_value = Ok(self._构造模型())
        实例 = AccessToken('AK', 'SK')
        实例.token()
        # 手动把缓存改为已过期
        实例._token_model = self._构造模型(过期时间=int(time.time()) - 100)
        mock_create.return_value = Ok(self._构造模型(token='TOKEN2'))
        结果 = 实例.token()
        self.assertEqual(结果.ok_value(), 'TOKEN2')
        self.assertEqual(mock_create.call_count, 2, '过期后应重新请求')

    @mock.patch('dsPyLib.ali.ali_access_token.AccessToken.create_token')
    def test_缓存有效时请求失败不影响缓存(self, mock_create):
        mock_create.return_value = Ok(self._构造模型())
        实例 = AccessToken('AK', 'SK')
        实例.token()
        mock_create.return_value = Err(ResultException('网络请求失败：连接被拒绝'))
        结果 = 实例.token()  # 缓存仍有效, 不应发起请求
        self.assertEqual(结果.ok_value(), 'TOKEN')
        self.assertEqual(mock_create.call_count, 1, '缓存有效时不应请求')

    @mock.patch('dsPyLib.ali.ali_access_token.AccessToken.create_token')
    def test_首次请求失败返回Err(self, mock_create):
        mock_create.return_value = Err(ResultException('网络请求失败：连接被拒绝'))
        实例 = AccessToken('AK', 'SK')
        结果 = 实例.token()
        self.assertTrue(结果.is_err())
        self.assertIsInstance(结果.err_value(), Exception)
        self.assertEqual(实例._token_model, None, '失败不应写入缓存')

    @mock.patch('dsPyLib.ali.ali_access_token.AccessToken.create_token')
    def test_不同实例独立缓存(self, mock_create):
        mock_create.return_value = Ok(self._构造模型())
        实例1 = AccessToken('AK1', 'SK1')
        实例2 = AccessToken('AK2', 'SK2')
        实例1.token()
        实例2.token()
        self.assertEqual(mock_create.call_count, 2, '不同实例应各自请求')


if __name__ == '__main__':
    unittest.main()
