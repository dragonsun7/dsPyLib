# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'

import os
import sys


def get_app_fullname():
    """
    获取所执行 Python 文件的路径(包括路径和文件全名)
    例如：/Users/ds/Documents/Develop/CCApps/main.py
    :return: str
    """
    return sys.argv[0]


def get_app_name():
    """
    返回所执行 Python 文件的名称(不包含后缀名)
    例如：main
    :return: str
    """
    main_file = sys.argv[0]
    return os.path.splitext(os.path.basename(main_file))[0]


def get_app_dir():
    """
    返回所执行 Python 文件所在路径(最后不带 / )
    例如：/Users/ds/Documents/Develop/CCApps
    :return: str
    """
    return os.path.dirname(get_app_fullname())


def 获取当前进程内存占用() -> int:  # 字节
    # 参考: https://saucer-man.com/operation_and_maintenance/298.html
    import psutil  # 需要安装psutil包

    pid = os.getpid()
    p = psutil.Process(pid)
    info = p.memory_full_info()
    return info.uss
