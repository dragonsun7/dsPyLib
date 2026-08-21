# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2026-08-19 08:01:38'

"""
    自定义 get 和 post 请求
    封装了常见的异常处理
"""

import json
from typing import Optional

import requests

from dsPyLib.类型.ds_rust_style_result import Result, Ok, Err, ResultException


def ds_get(url: str, params: Optional[dict] = None, **kwargs) -> Result[requests.Response, Exception]:
    """
    发起GET请求，封装了异常处理
    :param url:
    :param params:
    :return: 成功返回响应对象，失败返回异常对象
    """
    # 发起网络请求
    try:
        response = requests.get(url=url, params=params, timeout=10, **kwargs)  # 设置了10秒超时
        response.raise_for_status()  # 验证响应成功状态
    except requests.exceptions.RequestException as e:  # 网络层异常(连接失败/超时/DNS等)
        return Err(e)
    except Exception as e:
        return Err(e)

    return Ok(response)


def ds_post(url: str, data, headers: Optional[dict] = None, **kwargs) -> Result[requests.Response, Exception]:
    try:
        # 如果data传入的是字典，则需要转换为Json字符串
        if isinstance(data, dict):
            data = json.dumps(data)

        response = requests.post(url=url, data=data, headers=headers, timeout=10, **kwargs)  # 设置了10秒超时
    except requests.exceptions.RequestException as e:
        return Err(e)
    except Exception as e:
        return Err(e)

    return Ok(response)


def response_data_to_dict(response: requests.Response) -> Result[dict, Exception]:
    """
    将响应数据转为Json字典，如果不是字典则失败
    :param response: 响应对象
    :return: 成功返回字典，失败返回异常对象
    """
    # 拆解响应内容
    try:
        root = response.json()
    except (ValueError, requests.exceptions.RequestException) as e:
        # 覆盖:
        #   JSONDecodeError(ValueError子类)
        #   UnicodeDecodeError(ValueError子类)
        #   ContentDecodingError(内容解码或解压损坏, 属 RequestException)
        return Err(e)

    # 判断是否为dict
    if not isinstance(root, dict):
        return Err(ResultException('响应数据不是JSON字典！'))

    return Ok(root)

# def response_data_to_list(response: requests.Response) -> Result[list, Exception]:
#     pass
