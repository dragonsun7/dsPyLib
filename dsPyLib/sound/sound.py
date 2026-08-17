# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2019-08-23 14:26:29'

import threading
import wave

import pyaudio


def play_wav(file: str):
    """
    同步播放WAV文件 (需要引用pyaudio)
    :param file: WAV文件名
    """
    块大小 = 1024  # 每次读取/写入的帧数

    # 打开WAV文件(若文件不存在或不是WAV, 此处抛出异常, 无资源需要清理)
    音频文件 = wave.open(file, 'rb')
    try:
        # 实例化 PyAudio(若没有音频设备, 此处抛出异常, 音频文件由最外层 finally 关闭)
        音频设备 = pyaudio.PyAudio()
        try:
            音频格式 = 音频设备.get_format_from_width(音频文件.getsampwidth())
            声道数 = 音频文件.getnchannels()
            采样率 = 音频文件.getframerate()

            # 打开输出流(若打开失败, 音频设备由内层 finally 释放)
            输出流 = 音频设备.open(
                format=音频格式,
                channels=声道数,
                rate=采样率,
                frames_per_buffer=块大小,
                output=True
            )
            try:
                # 读取并播放音频数据
                音频数据 = 音频文件.readframes(块大小)
                while 音频数据:
                    输出流.write(音频数据)
                    音频数据 = 音频文件.readframes(块大小)
            finally:
                # 收尾流程(无论播放是否出错)
                输出流.stop_stream()
                输出流.close()
        finally:
            # 释放 PyAudio
            音频设备.terminate()
    finally:
        # 关闭 WAV 文件
        音频文件.close()


# 播放互斥锁: 保证同时只播放一段声音(线程安全, 无竞态)
_播放锁 = threading.Lock()


def play_wav_async(file: str) -> threading.Thread:
    """
    异步播放WAV文件 (需要引用pyaudio)
        注意：同时只能播放一段声音，后发起的播放会等待前一次播放完成
    :param file: WAV文件名
    :return: 播放线程对象, join() 会等待本次播放真正完成
    """

    def 播放():
        with _播放锁:
            play_wav(file)

    线程 = threading.Thread(target=播放)
    线程.daemon = True
    线程.start()
    return 线程
