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
                --log_file_prefix=/tmp/pysnowflake.log
        后台启动：
            nohup snowflake_start_server
                --address=127.0.0.1
                --port=8910
                --dc=1
                --worker=1
                --log_file_prefix=/tmp/pysnowflake.log
                >/dev/null &
        参数说明：
            --address：本机的IP地址，默认localhost
            --port：监听端口，默认8910
            --dc：数据中心唯一标识符，默认为0
            --worker：工作者唯一标识符，默认为0
            --log_file_prefix：日志文件所在位置
    使用(默认服务器 localhost:8910)：
        import snowflake.client
        guid = snowflake.client.get_guid()
        print(guid)

    服务器不在默认端口时的使用方法：
        snowflake.client.setup(host='127.0.0.1', port=18910)  # 切换服务器地址
        guid = snowflake.client.get_guid()
"""

import snowflake.client

if __name__ == '__main__':
    try:
        # snowflake.client.setup(host='localhost', port=8910)
        guid = snowflake.client.get_guid()
        print(guid)
    except Exception as e:
        print(f'获取雪花ID失败: {e}')
        print('提示: 请先按 docstring 中的命令启动 snowflake_start_server, 再运行本示例')
        exit(1)
