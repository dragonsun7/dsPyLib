# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-18 09:30:00'

"""
    dsPyLib/sound/sound.py 的单元测试
    play_wav 返回 Result: 成功 Ok(None), 失败 Err(异常), 不抛出异常;
    play_wav_async 的 complete_callback 参数为播放结果的 Result
    大部分用例 mock pyaudio, 不依赖真实音频设备; 用真实临时文件验证错误分类
"""

import os
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock

from dsPyLib.sound.sound import play_wav, play_wav_async
from dsPyLib.类型.ds_rust_style_result import Ok, Err


class 音频测试基类(unittest.TestCase):
    """提供公共的音频文件路径"""

    def setUp(self):
        self.音频文件 = str(Path(__file__).parent / 'notice.wav')
        self.错误的音频文件 = str(Path(__file__).parent / 'notice1.wav')


class 音频测试(音频测试基类):
    """真实播放(需音频设备)"""

    def test_同步播放音频(self):
        print('开始同步播放...', flush=True)
        结果 = play_wav(self.音频文件)
        self.assertTrue(结果.is_ok())
        print('同步播放完成！', flush=True)

    def test_同步播放音频_多次(self):
        print('开始同步播放第一个音频...', flush=True)
        self.assertTrue(play_wav(self.音频文件).is_ok())
        print('第一个音频同步播放完成！', flush=True)

        print('开始同步播放第二个音频...', flush=True)
        self.assertTrue(play_wav(self.音频文件).is_ok())
        print('第二个音频同步播放完成！', flush=True)

    def test_异步播放音频(self):
        print('开始异步播放...', flush=True)
        线程 = play_wav_async(self.音频文件)
        线程.join()
        print('异步播放调用完成！', 线程, flush=True)

    def test_异步播放音频_多次(self):
        print('开始异步播放第一个音频...', flush=True)
        线程1 = play_wav_async(self.音频文件)
        print('第一个音频异步播放调用完成！', 线程1, flush=True)

        print('开始异步播放第二个音频...', flush=True)
        线程2 = play_wav_async(self.音频文件)
        print('第二个音频异步播放调用完成！', 线程2, flush=True)

        线程1.join()
        线程2.join()

    def test_同步播放音频_错误的文件名(self):
        结果 = play_wav(self.错误的音频文件)
        self.assertTrue(结果.is_err())
        self.assertIsInstance(结果.err_value(), FileNotFoundError)

    def test_同步播放音频_文件名为空字符串(self):
        结果 = play_wav('')
        self.assertTrue(结果.is_err())
        self.assertIsInstance(结果.err_value(), FileNotFoundError)


class 错误处理测试(音频测试基类):
    """play_wav 各失败阶段的错误分类(不触发真实音频播放)"""

    def test_文件不存在返回Err(self):
        结果 = play_wav(str(Path(__file__).parent / '不存在.wav'))
        self.assertTrue(结果.is_err())
        self.assertIsInstance(结果.err_value(), FileNotFoundError)

    def test_空WAV文件返回Err(self):
        路径 = os.path.join(tempfile.gettempdir(), '测试空文件.wav')
        open(路径, 'w').close()
        try:
            结果 = play_wav(路径)
            self.assertTrue(结果.is_err())
            self.assertIsInstance(结果.err_value(), EOFError)
        finally:
            os.remove(路径)

    def test_非WAV文件返回Err(self):
        路径 = os.path.join(tempfile.gettempdir(), '测试非wav.txt')
        with open(路径, 'w') as f:
            f.write('这不是WAV文件')
        try:
            结果 = play_wav(路径)
            self.assertTrue(结果.is_err())
            self.assertIsInstance(结果.err_value(), wave.Error)
        finally:
            os.remove(路径)

    def test_路径是目录返回Err(self):
        结果 = play_wav(str(Path(__file__).parent))
        self.assertTrue(结果.is_err())
        self.assertIsInstance(结果.err_value(), IsADirectoryError)

    @mock.patch('dsPyLib.sound.sound.pyaudio.PyAudio')
    def test_音频设备初始化失败返回Err(self, mock_pa):
        # 文件已打开但设备初始化失败: 返回 Err 且文件由最外层 finally 关闭(无泄漏)
        mock_pa.side_effect = OSError('No output device')
        结果 = play_wav(self.音频文件)
        self.assertTrue(结果.is_err())
        self.assertIsInstance(结果.err_value(), OSError)

    @mock.patch('dsPyLib.sound.sound.pyaudio.PyAudio')
    def test_不支持的采样位宽返回Err(self, mock_pa):
        mock_pa.return_value.get_format_from_width.side_effect = ValueError('Invalid width')
        结果 = play_wav(self.音频文件)
        self.assertTrue(结果.is_err())
        self.assertIsInstance(结果.err_value(), ValueError)

    @mock.patch('dsPyLib.sound.sound.pyaudio.PyAudio')
    def test_播放中设备异常返回Err(self, mock_pa):
        流 = mock_pa.return_value.open.return_value
        流.write.side_effect = OSError('设备断开')
        结果 = play_wav(self.音频文件)
        self.assertTrue(结果.is_err())
        self.assertIsInstance(结果.err_value(), OSError)

    @mock.patch('dsPyLib.sound.sound.pyaudio.PyAudio')
    def test_清理异常返回Err不抛出(self, mock_pa):
        # 播放成功但清理失败: 契约要求返回 Err 而非从函数抛出
        流 = mock_pa.return_value.open.return_value
        流.close.side_effect = OSError('close失败')
        结果 = play_wav(self.音频文件)
        self.assertTrue(结果.is_err())


class 回调测试(音频测试基类):
    """play_wav_async 的 complete_callback(参数为播放结果的 Result)"""

    @mock.patch('dsPyLib.sound.sound.play_wav')
    def test_播放成功回调收到Ok(self, mock_play):
        """
        列表.append 本身就是一个可调用对象（Callable[[任意值], None]），正好符合 complete_callback 的签名，于是直接拿来当回调。
        它会把每次调用收到的参数（这里是 Result 对象）收集进列表——相当于一个"回调记录仪"：之后检查 回调记录 就知道回调被调了几次、每次收到什么。
        """
        mock_play.return_value = Ok(None)
        回调记录 = []
        线程 = play_wav_async(self.音频文件, complete_callback=回调记录.append)
        线程.join()
        self.assertEqual(len(回调记录), 1)
        self.assertTrue(回调记录[0].is_ok())
        mock_play.assert_called_once_with(self.音频文件)

    @mock.patch('dsPyLib.sound.sound.play_wav')
    def test_播放失败回调收到Err(self, mock_play):
        mock_play.return_value = Err(FileNotFoundError('找不到文件'))
        回调记录 = []
        线程 = play_wav_async(self.音频文件, complete_callback=回调记录.append)
        线程.join()
        self.assertEqual(len(回调记录), 1)
        结果 = 回调记录[0]
        self.assertTrue(结果.is_err())
        self.assertIsInstance(结果.err_value(), FileNotFoundError)

    @mock.patch('dsPyLib.sound.sound.play_wav')
    def test_不传回调也正常(self, mock_play):
        mock_play.return_value = Ok(None)
        线程 = play_wav_async(self.音频文件)
        线程.join()
        mock_play.assert_called_once_with(self.音频文件)


if __name__ == '__main__':
    unittest.main()
