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
    # define stream chunk
    chunk = 1024

    # open a wav format music
    wf = wave.open(file, 'rb')

    # instantiate PyAudio
    p = pyaudio.PyAudio()

    # open stream (output=True表示音频输出)
    fmt = p.get_format_from_width(wf.getsampwidth())
    channels = wf.getnchannels()
    rate = wf.getframerate()
    # print(f'format: {fmt}\nchannels: {channels}\nrate: {rate}')

    stream = p.open(format=fmt,
                    channels=channels,
                    rate=rate,
                    frames_per_buffer=chunk,
                    output=True)

    # read data & play stream
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()


g_playing_thread = None  # 拼音播放线程(同时只能播放一个音频)


def play_wav_async(file: str) -> threading.Thread:
    """
    异步播放WAV文件 (需要引用pyaudio)
        注意：同时只能播放一段声音，开始调用前需要等待前一次播放完成
    :param file: WAV文件名
    :return 播放线程对象
    """

    def play():
        global g_playing_thread
        if g_playing_thread and g_playing_thread.is_alive():
            g_playing_thread.join()
        g_playing_thread = threading.Thread(target=play_wav, args=(file,))  # 异步播放
        g_playing_thread.start()

    thread = threading.Thread(target=play)
    thread.start()
    return thread


if __name__ == '__main__':
    import os

    filename = os.path.join(os.path.dirname(__file__), '../res/notice.wav')
    print(f'播放文件：{filename}')

    print('开始同步播放...')
    play_wav(filename)
    print('同步播放完成！\n')

    print('开始异步播放1...')
    t1 = play_wav_async(filename)
    print('异步播放1调用完成！')

    print('开始异步播放2...')
    t2 = play_wav_async(filename)
    print('异步播放2调用完成！')
