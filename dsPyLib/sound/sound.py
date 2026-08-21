# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-08-23 14:26:29'

import threading
import wave
from typing import Callable, Optional

import pyaudio

from dsPyLib.类型.ds_rust_style_result import Result, Ok, Err


def play_wav(file: str) -> Result[str, Exception]:
    """
    同步播放WAV文件 (需要引用pyaudio)
    本函数不抛出异常 (为了异步播放的完成回调)
    :param file: WAV文件名
    :return: 成功返回 Ok(文件名); 失败返回 Err(异常);
    """

    def _play():
        音频文件 = wave.open(file, 'rb')
        try:
            音频设备 = pyaudio.PyAudio()  # 实例化 PyAudio(若没有音频设备, 此处抛出异常)
            try:
                块大小 = 1024  # 每次读取/写入的帧数
                音频格式 = 音频设备.get_format_from_width(音频文件.getsampwidth())
                声道数 = 音频文件.getnchannels()
                采样率 = 音频文件.getframerate()
                输出流 = 音频设备.open(format=音频格式, channels=声道数, rate=采样率, frames_per_buffer=块大小, output=True)  # 打开输出流
                try:
                    # 读取并播放音频数据
                    音频数据 = 音频文件.readframes(块大小)
                    while 音频数据:
                        输出流.write(音频数据)
                        音频数据 = 音频文件.readframes(块大小)
                finally:
                    输出流.stop_stream()
                    输出流.close()
            finally:
                音频设备.terminate()
        finally:
            音频文件.close()

    try:  # 一个最外层的try，用于捕获所有异常，保证本函数不抛出异常
        _play()
    except Exception as e:
        return Err(e)
    else:
        return Ok(file)


# 播放互斥锁: 保证同时只播放一段声音(线程安全, 无竞态)
_locker = threading.Lock()


def play_wav_async(file: str, complete_callback: Optional[Callable[[Result[str, Exception]], None]] = None) -> threading.Thread:
    """
    异步播放WAV文件 (需要引用pyaudio)
        注意：同时只能播放一段声音，后发起的播放会等待前一次播放完成
    :param file: WAV文件名
    :param complete_callback: 播放完成后的回调(无论成功或失败都会调用);
        回调参数为播放结果的 Result(成功为 Ok(文件名), 失败为 Err(异常));
        回调在播放线程内、释放播放锁之后执行(不会阻塞排队中的播放, 也可安全地在回调里再次播放)
    :return: 播放线程对象, join() 会等待本次播放真正完成
    """

    def _play():
        with _locker:
            result = play_wav(file)

        # 回调放在锁外: 回调里再播放(同步/异步)不会死锁, 也不会拖住排队中的播放
        if complete_callback:
            complete_callback(result)

    thread = threading.Thread(target=_play)
    thread.daemon = True
    thread.start()

    return thread
