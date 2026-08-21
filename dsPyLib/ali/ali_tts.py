# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-12-30 12:49:13'

import json
import os
import tempfile
import threading
import uuid
from pathlib import Path
from typing import Literal, TypeAlias

from dsPyLib.ali.ali_access_token import AccessToken
from dsPyLib.sound.sound import play_wav, play_wav_async
from dsPyLib.utils.ds_request import ds_get, ds_post
from dsPyLib.类型.ds_rust_style_result import Result, Ok, Err, ResultException

"""
    语音合成：文本 => 语音

    文档：
        https://help.aliyun.com/document_detail/94737.html?spm=a2c4g.11186623.6.597.340f259efJxFPB#h2-python-demo13
        https://help.aliyun.com/document_detail/72153.html?spm=a2c4g.11186623.2.32.5d375275hoibnU
        
    安装：
        pip install aliyun-python-sdk-core
        
    接口：
        主要使用：
            tts_to_file()
            play_tts_async()
            play_tts_sync()
"""

HTTPMethod: TypeAlias = Literal['GET', 'POST']


class AliTTS(object):

    def __init__(self, access_key_id: str, access_key_secret: str, tts_app_key: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.tts_app_key = tts_app_key

        self._access_token_obj = AccessToken(self.access_key_id, self.access_key_secret)
        self._host = 'nls-gateway.cn-shanghai.aliyuncs.com'
        self._url = f'https://{self._host}/stream/v1/tts'
        self._params = {
            'appkey': self.tts_app_key,
            'format': 'wav',  # format 支持设置合成音频的格式：pcm，wav，mp3
            'sample_rate': 16000,  # sample_rate 支持设置合成音频的采样率：8000Hz、16000Hz
            'voice': 'xiaoyun',  # voice 发音人，可选，默认是xiaoyun
            'volume': 50,  # volume 音量，范围是0~100，可选，默认50
            'speech_rate': 0,  # speech_rate 语速，范围是-500~500，可选，默认是0
            'pitch_rate': 0,  # pitch_rate 语调，范围是-500~500，可选，默认是0
        }

    def tts_to_file(self, text_data: str, file: str, method: HTTPMethod = 'POST') -> Result[str, Exception]:
        return self._request(text_data, file, method)

    def play_tts_sync(self, text_data: str, method: HTTPMethod = 'POST') -> Result[None, Exception]:
        temp_file = self._create_tempfile_path()
        try:
            result = self.tts_to_file(text_data, temp_file, method)
            if result.is_err():
                return Err(result.unwrap_err())

            result = play_wav(file=temp_file)
            if result.is_ok():
                return Ok(None)
            else:
                return Err(result.unwrap_err())
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def play_tts_async(self, text_data: str, method: HTTPMethod = 'POST') -> Result[threading.Thread, Exception]:
        temp_file = self._create_tempfile_path()

        # 播放完成后清除临时文件(无论成功失败)
        def complete_callback(_):
            if os.path.exists(temp_file):
                os.remove(temp_file)

        result = self.tts_to_file(text_data, temp_file, method)
        if result.is_err():
            return Err(result.unwrap_err())

        thread = play_wav_async(file=temp_file, complete_callback=complete_callback)
        return Ok(thread)

    # ---------- 私有 ---------- #

    @staticmethod
    def _create_tempfile_path() -> str:
        filename = f'tmp_ali_tts_{str(uuid.uuid4()).replace('-', '')}.wav'
        tmp_dir = Path(tempfile.gettempdir())
        tmp_file = str(tmp_dir / filename)
        return tmp_file

    def _request(self, text_data: str, file_path: str, method: HTTPMethod = 'POST') -> Result[str, Exception]:
        """
        请求生成语音
            单次调用传入文本不能超过300个字符，否则超过300个字符的内容会被截断，只合成300个字符以内的内容
        :param text_data: 要转换的文本
        :param file_path: 合成后语音文件路径
        :param method: 请求方法 'GET'、'POST'
        :return: 成功返回缓存的音频文件路径，失败返回错误信息
        """

        # 校验text长度
        if len(text_data) > 300:
            return Err(ResultException('要转换的文本太长(不能超过300字符)'))

        # 获取 Token
        result1 = self._access_token_obj.token()
        if result1.is_err():
            return Err(result1.unwrap_err())
        token = result1.unwrap()

        # 发送请求
        params = self._params.copy()
        params['token'] = token
        params['text'] = text_data
        if 'GET' == method:
            result = ds_get(url=self._url, params=params)
        elif 'POST' == method:
            result = ds_post(self._url, data=params, headers={'Content-Type': 'application/json'})
        else:
            return Err(ResultException('未能传入正确的请求方法'))

        # 获取响应
        if result.is_err():
            return Err(result.unwrap_err())
        response = result.unwrap()

        # 验证返回的内容正确
        content_type = response.headers.get('Content-Type', None)
        if 'audio/mpeg' != content_type:
            return Err(ResultException('返回的数据不正确！'))

        content = response.content
        try:
            with open(file_path, mode='wb') as f:
                f.write(content)
        except Exception as e:
            return Err(e)

        return Ok(file_path)
