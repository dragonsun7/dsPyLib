# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'


from dsPyLib.utils.decorator import *
from dsPyLib.utils.logging import *


@scheduler(count=3, interval=3, unit=CycleUnit.second)
def job1():
    logger.info('job1')


@scheduler(unit=CycleUnit.minute)
def job2():
    logger.info('job2')


if __name__ == '__main__':
    job1()
    job2()
    print('OK')
