# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-12-30 12:49:13'

import os
import uuid
import tempfile
import http.client
import urllib.parse
import json
from .ali_access_token import AccessToken
from ..sound.sound import play_wav, play_wav_async

"""
    语音合成：文本 => 语音

    文档：
        https://help.aliyun.com/document_detail/94737.html?spm=a2c4g.11186623.6.597.340f259efJxFPB#h2-python-demo13
        https://help.aliyun.com/document_detail/72153.html?spm=a2c4g.11186623.2.32.5d375275hoibnU
        
    安装：
        pip install aliyun-python-sdk-core
"""


class AliTTS(object):

    def __init__(self, app_key: str, access_token: str):
        # 对外属性
        self.app_key = app_key
        self.access_token = access_token
        self.format = 'wav'  # format 支持设置合成音频的格式：pcm，wav，mp3
        self.sample_rate = 16000  # sample_rate 支持设置合成音频的采样率：8000Hz、16000Hz
        self.voice = 'xiaoyun'  # voice 发音人，可选，默认是xiaoyun
        self.volume = 50  # volume 音量，范围是0~100，可选，默认50
        self.speech_rate = 0  # speech_rate 语速，范围是-500~500，可选，默认是0
        self.pitch_rate = 0  # pitch_rate 语调，范围是-500~500，可选，默认是0

        # 私有属性
        self._host = 'nls-gateway.cn-shanghai.aliyuncs.com'
        self._url = f'https://{self._host}/stream/v1/tts'

    def get(self, text_data: str, file_path: str) -> (bool, str):
        return self._request(text_data, file_path, 'GET')

    def post(self, text_data: str, file_path: str) -> (bool, str):
        return self._request(text_data, file_path, 'POST')

    # ---------- 私有 ---------- #

    def _request(self, text_data: str, file_path: str, method: str = 'POST') -> (bool, str):
        """
        请求生成语音
            单次调用传入文本不能超过300个字符，否则超过300字符的内容会被截断，只合成300字符以内的内容
        :param text_data: 要转换的文本
        :param file_path: 合成后语音文件路径
        :param method: 请求方法 'GET'、'POST'
        :return: 第一个参数是成功与否/第二个参数是错误说明(如果有的话)
        """
        conn = http.client.HTTPSConnection(self._host)
        try:
            # 请求
            if 'GET' == method:
                url = self._get_params(text_data)
                conn.request(method='GET', url=url)
            elif 'POST' == method:
                url = self._url
                body = self._post_params(text_data)
                http_headers = {'Content-Type': 'application/json'}
                conn.request(method='POST', url=url, body=body, headers=http_headers)
            else:
                return False, '请求方法不正确'

            # 响应
            response = conn.getresponse()

            if response.status != http.HTTPStatus.OK:
                return False, f'{response.status}, {response.reason}'

            content_type = response.getheader('Content-Type')
            body = response.read()
            if 'audio/mpeg' != content_type:
                return False, f'{str(body)}'

            with open(file_path, mode='wb') as f:
                f.write(body)
            return True, None
        finally:
            conn.close()

    # 生成GET请求参数
    def _get_params(self, text_data: str) -> str:
        # 采用RFC 3986规范进行url_encode编码
        text_url_encode = text_data
        text_url_encode = urllib.parse.quote_plus(text_url_encode)
        text_url_encode = text_url_encode.replace("+", "%20")
        text_url_encode = text_url_encode.replace("*", "%2A")
        text_url_encode = text_url_encode.replace("%7E", "~")

        url = self._url
        url = url + '?appkey=' + self.app_key
        url = url + '&token=' + self.access_token
        url = url + '&format=' + self.format
        url = url + '&sample_rate=' + str(self.sample_rate)
        url = url + '&voice=' + self.voice
        url = url + '&volume=' + str(self.volume)
        url = url + '&speech_rate=' + str(self.speech_rate)
        url = url + '&pitch_rate=' + str(self.pitch_rate)
        url = url + '&text=' + text_url_encode
        return url

    # 生成POST请求参数
    def _post_params(self, text_data: str) -> str:
        body = {
            'appkey': self.app_key,
            'token': self.access_token,
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


def tts_to_file(text_data: str, filename: str, access_key_id: str, access_key_secret: str, app_key: str) -> (bool, str):
    # 获取access token
    access_token, expire_time = AccessToken.create_token(access_key_id, access_key_secret)
    if not (access_token and expire_time):
        return False, '获取语音合成的access token失败！'

    # 合成播放文件
    ali_tts_obj = AliTTS(app_key=app_key, access_token=access_token)
    ok, msg = ali_tts_obj.post(text_data, filename)
    if not ok:
        return False, f'语音合成失败：{msg}'

    return True, None


def tts_async(text_data: str, access_key_id: str, access_key_secret: str, app_key: str) -> (bool, str):
    # 获取access token
    access_token, expire_time = AccessToken.create_token(access_key_id, access_key_secret)
    if not (access_token and expire_time):
        return False, '获取语音合成的access token失败！'

    # 播放
    temp_file = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()).replace('-', ''))
    ali_tts_obj = AliTTS(app_key=app_key, access_token=access_token)
    ok, msg = ali_tts_obj.post(text_data, temp_file)
    if not ok:
        return False, f'语音合成失败：{msg}'
    play_wav_async(temp_file)
    return True, None


def tts_sync(text_data: str, access_key_id: str, access_key_secret: str, app_key: str) -> (bool, str):
    # 获取access token
    access_token, expire_time = AccessToken.create_token(access_key_id, access_key_secret)
    if not (access_token and expire_time):
        return False, '获取语音合成的access token失败！'

    # 播放
    temp_file = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()).replace('-', ''))
    ali_tts_obj = AliTTS(app_key=app_key, access_token=access_token)
    ok, msg = ali_tts_obj.post(text_data, temp_file)
    try:
        if not ok:
            return False, f'语音合成失败：{msg}'
        else:
            play_wav(temp_file)
            return True, None
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == '__main__':
    # 这是一个示例
    g_access_key_id = '您的AccessKeyId'
    g_access_key_secret = '您的AccessKeySecret'
    g_app_key = '您的AppKey'
    g_access_token, g_expire_time = AccessToken.create_token(g_access_key_id, g_access_key_secret)
    if not (g_access_token and g_expire_time):
        print('获取语音合成的access token失败！')
        exit()

    g_text_data1 = '一：这是第一段内容'
    g_text_data2 = '二：这是第二段内容'

    temp_file1 = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()).replace('-', ''))
    temp_file2 = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()).replace('-', ''))
    ali_tts = AliTTS(app_key=g_app_key, access_token=g_access_token)
    ok1, msg1 = ali_tts.post(g_text_data1, temp_file1)
    ok2, msg2 = ali_tts.get(g_text_data2, temp_file2)
    try:
        if not ok1:
            print(f'第一段合成失败：{msg1}')
            exit()

        if not ok2:
            print(f'第二段合成失败：{msg2}')
            exit()

        print(f'同步播放第一段开始...')
        play_wav(temp_file1)
        print(f'同步播放第一段完成！')

        print(f'同步播放第二段开始...')
        play_wav(temp_file2)
        print(f'同步播放第二段完成！')

        print(f'异步播放第一段开始...')
        t1 = play_wav_async(temp_file1)
        print(f'异步播放第一段调用完成！')

        print(f'异步播放第二段开始...')
        t2 = play_wav_async(temp_file2)
        print(f'异步播放第二段调用完成！')

        t1.join()
        t2.join()
    finally:
        if os.path.exists(temp_file1):
            os.remove(temp_file1)
        if os.path.exists(temp_file2):
            os.remove(temp_file2)
