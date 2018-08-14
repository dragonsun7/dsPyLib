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


def init_logger():
    app_name = get_app_name()
    log_dir = get_app_dir() + '/logs'
    log_file = '%s/%s.log' % (log_dir, app_name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    ret = logging.getLogger(app_name)
    ret.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s[%(levelname)s]: %(funcName)s(%(filename)s:%(lineno)d) %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    # 一天一个日志文件，保留一年
    fh = logging.handlers.TimedRotatingFileHandler(log_file, when='D', interval=1, backupCount=365)
    fh.setLevel(logging.ERROR)
    fh.setFormatter(formatter)

    ret.addHandler(ch)
    ret.addHandler(fh)
    return ret


logger = init_logger()