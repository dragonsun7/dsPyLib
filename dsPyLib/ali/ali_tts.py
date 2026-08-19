# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-12-30 12:49:13'

import http.client
import json
import os
import tempfile
import threading
import uuid
from pathlib import Path
from urllib import parse

from dsPyLib.ali.ali_access_token import AccessToken
from dsPyLib.sound.sound import play_wav, play_wav_async
from dsPyLib.类型.ds_rust_style_result import Result, Ok, Err

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


class AliTTS(object):

    def __init__(self, access_key_id: str, access_key_secret: str, tts_app_key: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.tts_app_key = tts_app_key

        self.format = 'wav'  # format 支持设置合成音频的格式：pcm，wav，mp3
        self.sample_rate = 16000  # sample_rate 支持设置合成音频的采样率：8000Hz、16000Hz
        self.voice = 'xiaoyun'  # voice 发音人，可选，默认是xiaoyun
        self.volume = 50  # volume 音量，范围是0~100，可选，默认50
        self.speech_rate = 0  # speech_rate 语速，范围是-500~500，可选，默认是0
        self.pitch_rate = 0  # pitch_rate 语调，范围是-500~500，可选，默认是0

        self._host = 'nls-gateway.cn-shanghai.aliyuncs.com'
        self._url = f'https://{self._host}/stream/v1/tts'
        self._access_token_obj = AccessToken(self.access_key_id, self.access_key_secret)

    def get(self, text_data: str, file: str) -> Result[str, str]:
        return self._request(text_data, file, 'GET')

    def post(self, text_data: str, file: str) -> Result[str, str]:
        return self._request(text_data, file, 'POST')

    def tts_to_file(self, text_data: str, file: str) -> Result[str, str]:
        # 默认使用POST方式
        return self.post(text_data, file)

    def play_tts_async(self, text_data: str) -> Result[threading.Thread, str]:
        temp_file = self._create_tempfile_path()
        try:
            result = self.post(text_data, temp_file)
            if result.is_err():
                return Err(result.unwrap_err())

            thread = play_wav_async(temp_file)
            return Ok(thread)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def play_tts_sync(self, text_data: str) -> Result[None, str]:
        temp_file = self._create_tempfile_path()
        try:
            result = self.post(text_data, temp_file)
            if result.is_err():
                return Err(result.unwrap_err())

            play_wav(temp_file)
            return Ok(None)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    # ---------- 私有 ---------- #

    @staticmethod
    def _create_tempfile_path() -> str:
        filename = f'tmp_ali_tts_{str(uuid.uuid4()).replace('-', '')}.wav'
        tmp_dir = Path(tempfile.gettempdir())
        tmp_file = str(tmp_dir / filename)
        return tmp_file

    def _request(self, text_data: str, file_path: str, method: str = 'POST') -> Result[str, str]:
        """
        请求生成语音
            单次调用传入文本不能超过300个字符，否则超过300个字符的内容会被截断，只合成300个字符以内的内容
        :param text_data: 要转换的文本
        :param file_path: 合成后语音文件路径
        :param method: 请求方法 'GET'、'POST'
        :return: 成功返回缓存的音频文件路径，失败返回错误信息
        """

        # 获取 Token
        result1 = self._access_token_obj.token()
        if result1.is_ok():
            token = result1.unwrap()
        else:
            return Err(result1.unwrap_err())

        conn = http.client.HTTPSConnection(self._host)
        try:
            # 请求
            if 'GET' == method:
                url = self._get_params(text_data=text_data, token=token)
                conn.request(method='GET', url=url)
            elif 'POST' == method:
                url = self._url
                body = self._post_params(text_data=text_data, token=token)
                http_headers = {'Content-Type': 'application/json'}
                conn.request(method='POST', url=url, body=body, headers=http_headers)
            else:
                return Err('请求方法不正确')

            # 响应
            response = conn.getresponse()

            if response.status != http.HTTPStatus.OK:
                return Err(f'{response.status}, {response.reason}')

            content_type = response.getheader('Content-Type')
            body = response.read()
            if 'audio/mpeg' != content_type:
                return Err(f'{str(body)}')

            with open(file_path, mode='wb') as f:
                f.write(body)

            return Ok(file_path)
        finally:
            conn.close()

    # 生成GET请求参数
    def _get_params(self, text_data: str, token: str) -> str:
        # 采用RFC 3986规范进行url_encode编码
        text_url_encode = text_data
        text_url_encode = parse.quote_plus(text_url_encode)
        text_url_encode = text_url_encode.replace("+", "%20")
        text_url_encode = text_url_encode.replace("*", "%2A")
        text_url_encode = text_url_encode.replace("%7E", "~")

        url = self._url
        url = url + '?appkey=' + self.tts_app_key
        url = url + '&token=' + token
        url = url + '&format=' + self.format
        url = url + '&sample_rate=' + str(self.sample_rate)
        url = url + '&voice=' + self.voice
        url = url + '&volume=' + str(self.volume)
        url = url + '&speech_rate=' + str(self.speech_rate)
        url = url + '&pitch_rate=' + str(self.pitch_rate)
        url = url + '&text=' + text_url_encode
        return url

    # 生成POST请求参数
    def _post_params(self, text_data: str, token: str) -> str:
        body = {
            'appkey': self.tts_app_key,
            'token': token,
            'format': self.format,
            'sample_rate': self.sample_rate,
            'voice': self.voice,
            'volume': str(self.volume),
            'speech_rate': str(self.speech_rate),
            'pitch_rate': str(self.pitch_rate),
            'text': text_data
        }
        body = json.dumps(body)
        return body

# g_access_key_id = '您的AccessKeyId'
# g_access_key_secret = '您的AccessKeySecret'
# g_app_key = '您的AppKey'
#
#
# # 设置全局Keys
# def set_tts_keys(access_key_id: str, access_key_secret: str, app_key: str):
#     global g_access_key_id
#     global g_access_key_secret
#     global g_app_key
#     g_access_key_id = access_key_id
#     g_access_key_secret = access_key_secret
#     g_app_key = app_key
#
#
# # 设置全局Keys
# def set_tts_conf(conf_file: str):
#     """
#     配置文件需要包含如下内容：
#         [auth]
#         access_key_id=
#         access_key_secret=
#
#         [tts]
#         app_key=
#     """
#     config = configparser.ConfigParser()
#     config.read(conf_file)
#     ali_access_key_id = config['auth']['access_key_id']
#     ali_access_key_secret = config['auth']['access_key_secret']
#     tts_app_key = config['tts']['app_key']
#     set_tts_keys(ali_access_key_id, ali_access_key_secret, tts_app_key)
#
#
# def tts_sync2(s: str) -> Result:
#     return tts_sync(s, g_access_key_id, g_access_key_secret, g_app_key)
#
#
# def tts_async2(s: str) -> Result:
#     return tts_async(s, g_access_key_id, g_access_key_secret, g_app_key)
#
#
# if __name__ == '__main__':
#     # 从 dsConfigCenter 获取真实凭据
#     try:
#         from dsConfigCenter import config_center
#
#         ali = config_center.get_ali()
#         g_access_key_id = ali.access_key_id
#         g_access_key_secret = ali.access_key_secret
#         g_app_key = ali.tts_app_key
#     except Exception as e:
#         print(f'从 dsConfigCenter 获取阿里云凭据失败: {e}')
#         exit(1)
#
#     # 这是一个示例(会真实调用阿里云 TTS 并播放音频)
#     g_access_token, g_expire_time = AccessToken.create_token(g_access_key_id, g_access_key_secret)
#     if not (g_access_token and g_expire_time):
#         print('获取语音合成的access token失败！')
#         exit(1)
#
#     g_text_data1 = '一：这是第一段内容'
#     g_text_data2 = '二：这是第二段内容'
#
#     temp_file1 = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()).replace('-', ''))
#     temp_file2 = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()).replace('-', ''))
#     ali_tts = AliTTS(app_key=g_app_key, access_token=g_access_token)
#     ok1, msg1 = ali_tts.post(g_text_data1, temp_file1)
#     ok2, msg2 = ali_tts.get(g_text_data2, temp_file2)
#     try:
#         if not ok1:
#             print(f'第一段合成失败：{msg1}')
#             exit()
#
#         if not ok2:
#             print(f'第二段合成失败：{msg2}')
#             exit()
#
#         print(f'同步播放第一段开始...')
#         play_wav(temp_file1)
#         print(f'同步播放第一段完成！')
#
#         print(f'同步播放第二段开始...')
#         play_wav(temp_file2)
#         print(f'同步播放第二段完成！')
#
#         print(f'异步播放第一段开始...')
#         t1 = play_wav_async(temp_file1)
#         print(f'异步播放第一段调用完成！')
#
#         print(f'异步播放第二段开始...')
#         t2 = play_wav_async(temp_file2)
#         print(f'异步播放第二段调用完成！')
#
#         t1.join()
#         t2.join()
#     finally:
#         if os.path.exists(temp_file1):
#             os.remove(temp_file1)
#         if os.path.exists(temp_file2):
#             os.remove(temp_file2)
