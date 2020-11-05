# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2020-11-05 22:42:26'

import uuid


# 获取设备的唯一标识(12个字节)
def get_identifier() -> str:
    node = hex(uuid.getnode())
    node = node.lstrip('0x')
    node = node.zfill(12)
    return node


# uuid详情
def print_uuid_detail():
    u = uuid.uuid1()
    print(u)
    print(type(u))
    print('bytes   :', repr(u.bytes))
    print('hex     :', u.hex)
    print('int     :', u.int)
    print('urn     :', u.urn)
    print('variant :', u.variant)
    print('version :', u.version)
    print('fields  :', u.fields)
    print('\ttime_low            : ', u.time_low)
    print('\ttime_mid            : ', u.time_mid)
    print('\ttime_hi_version     : ', u.time_hi_version)
    print('\tclock_seq_hi_variant: ', u.clock_seq_hi_variant)
    print('\tclock_seq_low       : ', u.clock_seq_low)
    print('\tnode                : ', u.node)
    print('\ttime                : ', u.time)
    print('\tclock_seq           : ', u.clock_seq)
    print('\ttime_low            : ', hex(u.time_low))
    print('\ttime_mid            : ', hex(u.time_mid))
    print('\ttime_hi_version     : ', hex(u.time_hi_version))
    print('\tclock_seq_hi_variant: ', hex(u.clock_seq_hi_variant))
    print('\tclock_seq_low       : ', hex(u.clock_seq_low))
    print('\tnode                : ', hex(u.node))
    print('\ttime                : ', hex(u.time))
    print('\tclock_seq           : ', hex(u.clock_seq))


if __name__ == '__main__':
    print(get_identifier())
    print_uuid_detail()
