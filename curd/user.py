# -*- coding:utf-8 -*-
"""
@Time : 2022/5/5 11:04 AM
@Author: binkuolo
@Des: 用户表curd
"""
from models.base import User
from schemas.user import CreateUser


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


async def get_all_user():
    """
    获取所有管理员
    :return:
    """
    return await User.filter().all()

