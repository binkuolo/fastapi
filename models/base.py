# -*- coding:utf-8 -*-
"""
@Time : 2022/4/24 10:40 AM
@Author: binkuolo
@Des: 基础模型
"""

from tortoise import fields
from tortoise.models import Model


class TimestampMixin(Model):
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True


class User(TimestampMixin):
    role: fields.ManyToManyRelation["Role"] = \
        fields.ManyToManyField("base.Role", related_name="user", on_delete=fields.CASCADE)
    username = fields.CharField(null=True, max_length=20, description="用户名")
    user_type = fields.BooleanField(default=False, description="用户类型 True:超级管理员 False:普通管理员")
    password = fields.CharField(null=True, max_length=255)
    nickname = fields.CharField(default='binkuolo', max_length=255, description='昵称')
    user_phone = fields.CharField(null=True, description="手机号", max_length=11)
    user_email = fields.CharField(null=True, description='邮箱', max_length=255)
    full_name = fields.CharField(null=True, description='姓名', max_length=255)
    user_status = fields.IntField(default=0, description='0未激活 1正常 2禁用')
    header_img = fields.CharField(null=True, max_length=255, description='头像')
    sex = fields.IntField(default=0, null=True, description='0未知 1男 2女')
    remarks = fields.CharField(null=True, max_length=30, description="备注")
    client_host = fields.CharField(null=True, max_length=19, description="访问IP")

    class Meta:
        table_description = "用户表"
        table = "user"


class Role(TimestampMixin):
    user: fields.ManyToManyRelation[User]
    role_name = fields.CharField(max_length=15, description="角色名称")
    access: fields.ManyToManyRelation["Access"] = \
        fields.ManyToManyField("base.Access", related_name="role", on_delete=fields.CASCADE)
    role_status = fields.BooleanField(default=False, description="True:启用 False:禁用")
    role_desc = fields.CharField(null=True, max_length=255, description='角色描述')

    class Meta:
        table_description = "角色表"
        table = "role"


class Access(TimestampMixin):
    role: fields.ManyToManyRelation[Role]
    access_name = fields.CharField(max_length=15, description="权限名称")
    parent_id = fields.IntField(default=0, description='父id')
    scopes = fields.CharField(unique=True, max_length=255, description='权限范围标识')
    access_desc = fields.CharField(null=True, max_length=255, description='权限描述')
    menu_icon = fields.CharField(null=True, max_length=255, description='菜单图标')
    is_check = fields.BooleanField(default=False, description='是否验证权限 True为验证 False不验证')
    is_menu = fields.BooleanField(default=False, description='是否为菜单 True菜单 False不是菜单')

    class Meta:
        table_description = "权限表"
        table = "access"


class AccessLog(TimestampMixin):
    user_id = fields.IntField(description="用户ID")
    target_url = fields.CharField(null=True, description="访问的url", max_length=255)
    user_agent = fields.CharField(null=True, description="访问UA", max_length=255)
    request_params = fields.JSONField(null=True, description="请求参数get|post")
    ip = fields.CharField(null=True, max_length=32, description="访问IP")
    note = fields.CharField(null=True, max_length=255, description="备注")

    class Meta:
        table_description = "用户操作记录表"
        table = "access_log"
