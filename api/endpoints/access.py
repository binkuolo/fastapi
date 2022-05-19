# -*- coding:utf-8 -*-
"""
@Time : 2022/5/18 1:03 AM
@Author: binkuolo
@Des: 权限管理
"""
from fastapi import APIRouter, Security
from tortoise.queryset import F
from core.Auth import check_permissions
from core.Response import fail, success
from schemas import role, base
from models.base import Role, Access

router = APIRouter(prefix='/access')


@router.post('', summary="权限创建", response_model=base.BaseResp)
async def create_access(post: role.CreateAccess):
    """
    创建权限
    :param post: CreateAccess
    :return:
    """
    # 超级管理员可以创建权限
    # if req.state.user_id is not 1 and req.state.user_type is not False:
    #     return fail(msg="无法建权限!")

    check = await Access.get_or_none(scopes=post.scopes)
    if check:
        return fail(msg=f"scopes:{post.scopes} 已经存在!")
    result = await Access.create(**post.dict())
    if not result:
        return fail(msg="创建成功!")
    return success(msg=f"权限 {result.pk} 创建成功!")


@router.get('', summary="权限查询", dependencies=[Security(check_permissions, scopes=["role_access"])])
async def get_all_access(role_id: int):
    """
    获取全部权限
    :return:
    """
    result = await Access.annotate(key=F('id'), title=F('access_name')).all() \
        .values("key", "title", "parent_id")
    # 当前角色权限
    role_access = await Access.filter(role__id=role_id).values_list('id')

    # 系统权限
    tree_data = access_tree(result, 0)
    # 角色权限
    role_access = [i[0] for i in role_access]
    data = {
        "all_access": tree_data,
        "role_access": role_access
    }
    return success(msg="当前用户可以下发的权限", data=data)


@router.put('', summary="权限设置",
            dependencies=[Security(check_permissions, scopes=["role_access"])], response_model=base.BaseResp)
async def set_role_access(post: role.SetAccess):
    """
    设置角色权限
    :param post:
    :return:
    """
    # 获取当前角色
    role_data = await Role.get_or_none(id=post.role_id)
    # 无设置权限时清空权限
    if not post.access:
        await role_data.access.clear()
        return success(msg="已清空当前角色权限!")
    # 获取分配的权限集合
    access = await Access.filter(id__in=post.access, is_check=True).all()
    # 添加权限
    await role_data.access.add(*access)
    return success(msg="保存成功!")


def access_tree(data, pid):
    """
    遍历权限树
    :param data: rule[]
    :param pid: 父ID
    :return: list
    """
    result = []
    for item in data:
        if pid == item["parent_id"]:
            temp = access_tree(data, item["key"])
            if len(temp) > 0:
                # item["key"] = str(item["key"])
                item["children"] = temp
            result.append(item)
    return result
