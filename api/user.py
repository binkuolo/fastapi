# -*- coding:utf-8 -*-
"""
@Time : 2022/4/27 5:24 PM
@Author: binkuolo
@Des: 用户管理
"""
from core.Response import success, fail
from validator.user import CreateUser
from models.base import User, Role, Access
from core.Utils import en_password


async def user_info(user_id: int):
    """
    获取用户信息
    :param user_id: int
    :return:
    """
    user_data = await User.get_or_none(pk=user_id)
    if not user_data:
        return fail(msg=f"用户ID{user_id}不存在!")
    return success(msg="用户信息", data=user_data)


async def user_add(post: CreateUser):
    """
    创建用户
    :param post: CreateUser
    :return:
    """
    post.password = en_password(post.password)
    create_user = await User.create(**post.dict())
    if not create_user:
        return fail(msg=f"用户{post.username}创建失败!")
    return success(msg=f"用户{create_user.username}创建成功")


async def user_del(user_id: int):
    """
    删除用户
    :param user_id: int
    :return:
    """
    delete_user = await User.filter(pk=user_id).delete()
    if not delete_user:
        return fail(msg=f"用户{user_id}删除失败!")
    return success(msg="删除成功")


async def get_user_rules(user_id: int):
    """
    获取用户权限集合
    :param user_id:
    :return:
    """

    # 查询当前用户拥有的角色
    user_role = await Role.filter(user__id=user_id).values("role_name")
    # 查询当前用户的所有权限
    user_access_list = await Access.filter(role__user__id=user_id, is_check=True).values("id", "scopes")
    # 验证当前用户对当前域是否有权限
    is_pass = await Access.get_or_none(role__user__id=user_id, is_check=True, scopes="article_push", role__role_status=True)
    data = {
        "user_role": user_role,
        "pass": True if is_pass else False,
        "user_access_list": user_access_list
    }
    return success(msg="用户权限", data=data)
