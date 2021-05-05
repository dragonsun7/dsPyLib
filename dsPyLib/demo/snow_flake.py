# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2021-04-30 20:32:34'

"""
    雪花算法(用于生成唯一ID)
    https://www.pythonheidong.com/blog/article/496447/d0d2ef46be5ccac06417/
    
    安装：
        pip install pysnowflake
    启动：
        前台启动：
            snowflake_start_server
                --address=0.0.0.0
                --port=8910
                --dc=1
                --worker=1
                --log_file_prefix=/tmp/pysnowflask.log
        后台启动：
            nohup snowflake_start_server
                --address=127.0.0.1
                --port=8910 
                --dc=1 
                --worker=1 
                --log_file_prefix=/tmp/pysnowflask.log
                >/dev/null &
        参数说明：                
            —address：本机的IP地址默认localhost
            —dc：数据中心唯一标识符默认为0
            —worker：工作者唯一标识符默认为0
            —log_file_prefix：日志文件所在位置
    使用：
        import snowflake.client
        guid = snowflake.client.get_guid()
        print(guid)
"""

import snowflake.client

if __name__ == '__main__':
    guid = snowflake.client.get_guid()
    print(guid)
