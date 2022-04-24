# -*- coding:utf-8 -*-
"""
@Time : 2022/4/24 10:11 AM
@Author: binkuolo
@Des: 常用返回类型封装
"""
from typing import List


def res_antd(data: List = None, total: int = 0, code: bool = True):
    """
    支持ant-design-table 返回的格式
    :param code:
    :param data:
    :param total:
    :return:
    """
    if data is None:
        data = []
    result = {
        "success": code,
        "data": data,
        "total": total
    }
    return result


def base_response(code, msg, data=None):
    """基础返回格式"""
    if data is None:
        data = []
    result = {
        "code": code,
        "message": msg,
        "data": data
    }
    return result


def success(data=None, msg=''):
    """成功返回格式"""
    return base_response(200, msg, data)


def fail(code=-1, msg='', data=None):
    """失败返回格式"""
    return base_response(code, msg, data)