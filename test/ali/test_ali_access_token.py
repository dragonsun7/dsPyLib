# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-17 17:30:00'

"""
    dsPyLib/ali/ali_access_token.py 的单元测试
    阿里云凭据从 dsConfigCenter 获取；网络请求均 mock，不发起真实调用
"""

import unittest

from dsConfigCenter import config_center

from dsPyLib.ali.ali_access_token import AccessToken


class TestCreateToken(unittest.TestCase):

    def test_生成真实Token(self):
        ali = config_center.get_ali()
        token, expire_time = AccessToken.create_token(access_key_id=ali.access_key_id, access_key_secret=ali.access_key_secret)
        print(token, expire_time)
        self.assertIsInstance(token, str)
        self.assertIsInstance(expire_time, int)


if __name__ == '__main__':
    unittest.main()
