# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'

"""
    输出日志到当前的logs目录下，一天一个日志文件，保留一年
    使用方法：
        from dsPyLib.utils.logging import *
        
        logger.info(data)
        logger.error(err)
        ...
"""

import logging.handlers
from dsPyLib.utils.misc import *


def init_logger_with_level(stream_level=logging.DEBUG, file_level=logging.ERROR):
    app_name = get_app_name()
    log_dir = get_app_dir() + '/logs'
    log_file = '%s/%s.log' % (log_dir, app_name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter('%(asctime)s[%(levelname)s]: %(funcName)s(%(filename)s:%(lineno)d) %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(stream_level)
    ch.setFormatter(formatter)

    # 一天一个日志文件，保留一年
    fh = logging.handlers.TimedRotatingFileHandler(log_file, when='D', interval=1, backupCount=365)
    fh.setLevel(file_level)
    fh.setFormatter(formatter)

    ret = logging.getLogger(app_name)
    ret.setLevel(stream_level)
    ret.addHandler(ch)
    ret.addHandler(fh)
    return ret


def init_console_logger_with_level(level=logging.DEBUG):
    formatter = logging.Formatter('%(asctime)s[%(levelname)s]: %(funcName)s(%(filename)s:%(lineno)d) %(message)s')

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)

    app_name = get_app_name()
    ret = logging.getLogger(app_name)
    ret.setLevel(level)
    ret.addHandler(handler)
    return ret


def init_logger():
    return init_console_logger_with_level(logging.INFO)

    # 暂时不用文件日志，有文件系统权限问题未解决(因为macOS下获取日志文件路径有问题)
    # return init_logger_with_level(logging.INFO, logging.INFO)


logger = init_logger()
