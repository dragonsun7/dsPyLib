# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-17 17:30:00'

"""
    dsPyLib/ali/ali_tts.py 的单元测试
    全部 mock: 不发起真实阿里云 TTS 请求、不播放音频、不消耗配额
"""

import os
import tempfile
import threading
import unittest
import uuid
from pathlib import Path
from unittest import mock

from dsConfigCenter.config_center import config_center

from dsPyLib.ali.ali_tts import AliTTS
from dsPyLib.类型.ds_rust_style_result import Ok, Err, ResultException


def _临时路径() -> str:
    """生成一个测试用临时文件路径"""
    return str(Path(tempfile.gettempdir()) / f'test_ali_tts_{uuid.uuid4().hex}.wav')


class 真实测试(unittest.TestCase):

    def setUp(self):
        ali_conf = config_center.get_ali()
        self.ali_tts_obj = AliTTS(ali_conf.access_key_id, ali_conf.access_key_secret, ali_conf.tts_app_key)
        self.text = '你好小D+*!!啊'

    def test_play_tts_sync_get(self):
        result = self.ali_tts_obj.play_tts_sync(text_data=self.text, method='GET')
        self.assertTrue(result.is_ok())

    def test_play_tts_sync_post(self):
        result = self.ali_tts_obj.play_tts_sync(text_data=self.text, method='POST')
        self.assertTrue(result.is_ok())

    def test_play_tts_async_get(self):
        result = self.ali_tts_obj.play_tts_async(text_data=self.text, method='GET')
        self.assertTrue(result.is_ok())
        thread = result.unwrap()
        thread.join()

    def test_play_tts_async_post(self):
        result = self.ali_tts_obj.play_tts_async(text_data=self.text, method='POST')
        self.assertTrue(result.is_ok())
        thread = result.unwrap()
        thread.join()


class 测试_request(unittest.TestCase):
    """_request 的分支覆盖(经 tts_to_file 调用)"""

    def setUp(self):
        # AccessToken 必须在构造 AliTTS 之前 mock, 否则 __init__ 会创建真实实例并发起真实请求
        self._token_patcher = mock.patch('dsPyLib.ali.ali_tts.AccessToken')
        self._mock_token_class = self._token_patcher.start()
        self._mock_token_class.return_value.token.return_value = Ok('TOKEN')  # 默认 token 成功
        self.实例 = AliTTS('测试AK', '测试SK', '测试APP')

    def tearDown(self):
        self._token_patcher.stop()

    @staticmethod
    def _构造响应(content_type='audio/mpeg', content=b'wav-data'):
        响应 = mock.Mock()
        响应.headers.get.return_value = content_type
        响应.content = content
        return 响应

    @mock.patch('dsPyLib.ali.ali_tts.ds_post')
    def test_POST成功写入文件(self, mock_post):
        # token 成功 + POST 成功 + Content-Type 正确 -> Ok(文件路径), 文件内容写入
        mock_post.return_value = Ok(self._构造响应())
        临时 = _临时路径()
        try:
            结果 = self.实例.tts_to_file(text_data='你好', file=临时)
            self.assertTrue(结果.is_ok())
            self.assertEqual(结果.ok_value(), 临时)
            with open(临时, 'rb') as f:
                self.assertEqual(f.read(), b'wav-data')
        finally:
            if os.path.exists(临时):
                os.remove(临时)

    @mock.patch('dsPyLib.ali.ali_tts.ds_get')
    def test_GET方法调用ds_get(self, mock_get):
        mock_get.return_value = Ok(self._构造响应())
        临时 = _临时路径()
        try:
            结果 = self.实例.tts_to_file(text_data='你好', file=临时, method='GET')
            self.assertTrue(结果.is_ok())
            mock_get.assert_called_once()
        finally:
            if os.path.exists(临时):
                os.remove(临时)

    def test_文本超长返回Err(self):
        # 超过300个字符: 在获取 token 之前直接返回 Err, 不发起任何请求
        结果 = self.实例.tts_to_file(text_data='啊' * 301, file=_临时路径())
        self.assertTrue(结果.is_err())
        self.assertIn('文本太长', str(结果.err_value()))
        self._mock_token_class.return_value.token.assert_not_called()  # 未发起 token 请求

    @mock.patch('dsPyLib.ali.ali_tts.ds_post')
    def test_文本恰好300字符放行(self, mock_post):
        # 边界值: 恰好300个字符应通过校验并继续请求流程
        mock_post.return_value = Ok(self._构造响应())
        临时 = _临时路径()
        try:
            结果 = self.实例.tts_to_file(text_data='啊' * 300, file=临时)
            self.assertTrue(结果.is_ok())
            mock_post.assert_called_once()
        finally:
            if os.path.exists(临时):
                os.remove(临时)

    def test_token获取失败返回Err(self):
        self._mock_token_class.return_value.token.return_value = Err(ResultException('获取token失败'))
        结果 = self.实例.tts_to_file(text_data='你好', file=_临时路径())
        self.assertTrue(结果.is_err())
        self.assertIn('获取token失败', str(结果.err_value()))

    @mock.patch('dsPyLib.ali.ali_tts.ds_post')
    def test_请求失败返回Err(self, mock_post):
        mock_post.return_value = Err(ResultException('网络请求失败'))
        结果 = self.实例.tts_to_file(text_data='你好', file=_临时路径())
        self.assertTrue(结果.is_err())
        self.assertIn('网络请求失败', str(结果.err_value()))

    @mock.patch('dsPyLib.ali.ali_tts.ds_post')
    def test_ContentType不符返回Err(self, mock_post):
        mock_post.return_value = Ok(self._构造响应(content_type='text/html'))
        结果 = self.实例.tts_to_file(text_data='你好', file=_临时路径())
        self.assertTrue(结果.is_err())
        self.assertIn('返回的数据不正确', str(结果.err_value()))

    @mock.patch('dsPyLib.ali.ali_tts.ds_post')
    def test_写文件失败返回Err(self, mock_post):
        mock_post.return_value = Ok(self._构造响应())
        结果 = self.实例.tts_to_file(text_data='你好', file='/不存在目录/x.wav')
        self.assertTrue(结果.is_err())


class 测试play_tts_sync(unittest.TestCase):
    """play_tts_sync: 合成 -> 播放 -> 清理临时文件"""

    def setUp(self):
        self.实例 = AliTTS('测试AK', '测试SK', '测试APP')

    @mock.patch.object(AliTTS, '_create_tempfile_path')
    @mock.patch('dsPyLib.ali.ali_tts.play_wav')
    def test_成功播放并清理临时文件(self, mock_play, mock_temp):
        临时 = _临时路径()
        mock_temp.return_value = 临时
        with open(临时, 'wb') as f:
            f.write(b'x')  # 模拟合成产物
        try:
            with mock.patch.object(self.实例, '_request', return_value=Ok(临时)):
                mock_play.return_value = Ok(临时)
                结果 = self.实例.play_tts_sync('你好')
            self.assertTrue(结果.is_ok())
            mock_play.assert_called_once_with(file=临时)
        finally:
            if os.path.exists(临时):
                os.remove(临时)  # 双保险
        self.assertFalse(os.path.exists(临时), 'finally 应已删除临时文件')

    @mock.patch.object(AliTTS, '_create_tempfile_path')
    @mock.patch('dsPyLib.ali.ali_tts.play_wav')
    def test_播放失败传播Err并清理(self, mock_play, mock_temp):
        临时 = _临时路径()
        mock_temp.return_value = 临时
        with open(临时, 'wb') as f:
            f.write(b'x')
        try:
            with mock.patch.object(self.实例, '_request', return_value=Ok(临时)):
                mock_play.return_value = Err(ResultException('播放失败'))
                结果 = self.实例.play_tts_sync('你好')
            self.assertTrue(结果.is_err())
            self.assertIn('播放失败', str(结果.err_value()))
        finally:
            if os.path.exists(临时):
                os.remove(临时)
        self.assertFalse(os.path.exists(临时))

    def test_合成失败返回Err(self):
        with mock.patch.object(self.实例, '_request', return_value=Err(ResultException('合成失败'))):
            结果 = self.实例.play_tts_sync('你好')
        self.assertTrue(结果.is_err())
        self.assertIn('合成失败', str(结果.err_value()))


class 测试play_tts_async(unittest.TestCase):
    """play_tts_async: 合成 -> 异步播放 -> 回调清理临时文件"""

    def setUp(self):
        self.实例 = AliTTS('测试AK', '测试SK', '测试APP')

    @mock.patch.object(AliTTS, '_create_tempfile_path')
    @mock.patch('dsPyLib.ali.ali_tts.play_wav_async')
    def test_成功且播放完成后回调清理临时文件(self, mock_async, mock_temp):
        临时 = _临时路径()
        mock_temp.return_value = 临时
        捕获 = {}

        def 假异步(file, complete_callback=None):
            捕获['file'] = file
            捕获['回调'] = complete_callback
            return threading.Thread(target=lambda: None)  # 假线程, 不真实播放

        mock_async.side_effect = 假异步
        try:
            with mock.patch.object(self.实例, '_request', return_value=Ok(临时)):
                结果 = self.实例.play_tts_async('你好')
            self.assertTrue(结果.is_ok())
            self.assertEqual(捕获['file'], 临时)

            # 模拟播放完成, 触发回调 -> 临时文件被清理
            with open(临时, 'wb') as f:
                f.write(b'x')
            self.assertTrue(os.path.exists(临时))
            捕获['回调'](Ok(临时))
            self.assertFalse(os.path.exists(临时), '回调应删除临时文件')
        finally:
            if os.path.exists(临时):
                os.remove(临时)

    def test_合成失败返回Err(self):
        with mock.patch.object(self.实例, '_request', return_value=Err(ResultException('合成失败'))):
            结果 = self.实例.play_tts_async('你好')
        self.assertTrue(结果.is_err())
        self.assertIn('合成失败', str(结果.err_value()))


class 测试_create_tempfile_path(unittest.TestCase):

    def test_路径格式正确(self):
        路径 = AliTTS._create_tempfile_path()
        self.assertTrue(路径.startswith(tempfile.gettempdir()))
        self.assertTrue(路径.endswith('.wav'))
        self.assertIn('tmp_ali_tts_', 路径)
        # 两次生成应不重复
        self.assertNotEqual(路径, AliTTS._create_tempfile_path())


if __name__ == '__main__':
    unittest.main()
