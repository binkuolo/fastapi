# -*- coding:utf-8 -*-
"""
@Time : 2022/4/27 5:24 PM
@Author: binkuolo
@Des: 用户管理
"""
from core.Response import success, fail, res_antd
from schemas.user import CreateUser, AccountLogin, UserInfo
from core.Utils import en_password, check_password
from core.Auth import create_access_token
from fastapi import Request
from curd.user import get_one_user, add_user, get_user_for_username, delete_user, get_all_user
from config import settings


async def user_list(
        size: int = 10,
        current: int = 1,
        username: str = None
):
    """
    获取所有管理员
    :return:
    """
    data, total = await get_all_user(size, current)
    return res_antd(code=True, data=data, total=total)
    # return success(msg="管理员列表", data=user_list_data)


async def user_info(req: Request):
    """
    获取当前登陆用户信息
    :return:
    """
    user_data = await get_one_user(req.state.user_id)
    if not user_data:
        return fail(msg=f"用户ID{req.state.user_id}不存在!")
    return success(msg="用户信息", data=UserInfo(**user_data.__dict__))


async def user_add(post: CreateUser):
    """
    创建用户
    :param post: CreateUser
    :return:
    """
    get_user = await get_user_for_username(username=post.username)
    if get_user:
        return fail(msg=f"用户名{post.username}已经存在!")
    post.password = en_password(post.password)
    create_user = await add_user(post)
    if not create_user:
        return fail(msg=f"用户{post.username}创建失败!")
    return success(msg=f"用户{create_user.username}创建成功")


async def user_del(user_id: int):
    """
    删除用户
    :param user_id: int
    :return:
    """
    delete_action = await delete_user(user_id)
    if not delete_action:
        return fail(msg=f"用户{user_id}删除失败!")
    return success(msg="删除成功")


async def account_login(post: AccountLogin):
    """
    用户登陆
    :param post:
    :return: jwt token
    """
    get_user = await get_user_for_username(username=post.username)
    if not get_user:
        return fail(msg=f"用户{post.username}密码验证失败!")
    if not check_password(post.password, get_user.password):
        return fail(msg=f"用户{post.username}密码验证失败!")
    if not get_user.user_status:
        return fail(msg=f"用户{post.username}已被管理员禁用!")
    jwt_data = {
        "user_id": get_user.pk,
        "user_type": get_user.user_type
    }
    jwt_token = create_access_token(data=jwt_data)
    data = {"token": jwt_token, "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60}
    return success(msg="登陆成功😄", data=data)
