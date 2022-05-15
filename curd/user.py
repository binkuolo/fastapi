# -*- coding:utf-8 -*-
"""
@Time : 2022/5/5 11:04 AM
@Author: binkuolo
@Des: 用户表curd
"""
from typing import Dict, Union, List

from models.base import User
from schemas.user import CreateUser
from tortoise.queryset import F


async def get_one_user(user_id: int):
    """
    查询一个管理员
    :param user_id:
    :return:
    """
    return await User.get_or_none(pk=user_id)


async def get_user_for_username(username: str):
    """
    查询一个管理员
    :param username:
    :return:
    """
    return await User.get_or_none(username=username)


async def add_user(data: CreateUser):
    """
    添加管理员
    :param data:
    :return:
    """
    return await User.create(**data.dict())


async def delete_user(user_id: int):
    """
    删除管理员
    :param user_id:
    :return:
    """
    return await User.filter(pk=user_id).delete()


async def get_all_user(
        size: int = 10,
        current: int = 1,
):
    """
    获取所有管理员
    :return:
    """
    # 查询条件
    query = {}
    # if kwargs:
    #     query.setdefault('username', username)
    user = User.annotate(key=F("id")).filter(**query).filter(id__not=1).all()
    # 总数
    total = await user.count()
    # 查询
    data = await user.limit(size).offset(size * (current - 1)).order_by("-create_time") \
        .values(
        "key", "username", "user_type", "user_phone", "user_email",
        "user_status", "header_img", "sex", "remarks")

    return data, total
