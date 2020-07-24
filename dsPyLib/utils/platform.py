# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-07-24 20:13:40'

import platform


def is_windows() -> bool:
    return platform.system() == 'Windows'


if __name__ == '__main__':
    print(f'platform.machine()={platform.machine()}')
    print(f'platform.node()={platform.node()}')
    print(f'platform.platform()={platform.platform()}')
    print(f'platform.processor()={platform.processor()}')
    print(f'platform.python_build()={platform.python_build()}')
    print(f'platform.python_compiler()={platform.python_compiler()}')
    print(f'platform.python_branch()={platform.python_branch()}')
    print(f'platform.python_implementation()={platform.python_implementation()}')
    print(f'platform.python_revision()={platform.python_revision()}')
    print(f'platform.python_version()={platform.python_version()}')
    print(f'platform.python_version_tuple()={platform.python_version_tuple()}')
    print(f'platform.system()={platform.system()}')
    print(f'platform.release()={platform.release()}')
    print(f'platform.version()={platform.version()}')
    print(f'platform.system_alias()={platform.system_alias(platform.system(), platform.release(), platform.version())}')
    print(f'platform.uname()={platform.uname()}')
