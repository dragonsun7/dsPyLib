# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-18 09:30:00'

"""
    dsPyLib/sound/sound.py 的单元测试
    pyaudio 全部 mock, 不依赖真实音频设备; 用真实临时 WAV 文件验证读取逻辑
"""

import unittest
from pathlib import Path

from dsPyLib.sound.sound import play_wav, play_wav_async


class 音频测试(unittest.TestCase):

    def setUp(self):
        self.音频文件 = str(Path(__file__).parent / 'notice.wav')
        self.错误的音频文件 = str(Path(__file__).parent / 'notice1.wav')

    def test_同步播放音频(self):
        print('开始同步播放...', flush=True)
        play_wav(self.音频文件)
        print('同步播放完成！', flush=True)

    def test_同步播放音频_多次(self):
        print('开始同步播放第一个音频...', flush=True)
        play_wav(self.音频文件)
        print('第一个音频同步播放完成！', flush=True)

        print('开始同步播放第二个音频...', flush=True)
        play_wav(self.音频文件)
        print('第二个音频同步播放完成！', flush=True)

    def test_异步播放音频(self):
        print('开始异步播放...', flush=True)
        线程 = play_wav_async(self.音频文件)
        线程.join()
        print('异步播放调用完成！', 线程, flush=True)

    def test_异步播放音频_多次(self):
        print('开始异步播放第一个音频...', flush=True)
        线程1 = play_wav_async(self.音频文件)
        线程1.join()
        print('第一个音频异步播放调用完成！', 线程1, flush=True)

        print('开始异步播放第二个音频...', flush=True)
        线程2 = play_wav_async(self.音频文件)
        线程2.join()
        print('第二个音频异步播放调用完成！', 线程2, flush=True)

    def test_同步播放音频_错误的文件名(self):
        with self.assertRaises(FileNotFoundError):
            play_wav(self.错误的音频文件)

    def test_同步播放音频_文件名为空字符串(self):
        with self.assertRaises(FileNotFoundError):
            play_wav('')


if __name__ == '__main__':
    unittest.main()
