# -*- coding:utf-8 -*-
"""
@Time : 2022/4/27 5:29 PM
@Author: binkuolo
@Des: 用户验证模型
"""
from pydantic import Field, BaseModel
from typing import Optional


class CreateUser(BaseModel):
    username: str = Field(min_length=3, max_length=10)
    password: str = Field(min_length=8, max_length=12)


class AccountLogin(BaseModel):
    username: str = Field(min_length=3, max_length=10)
    password: str = Field(min_length=8, max_length=12)


class UserInfo(BaseModel):
    id: int
    username: str
    age: Optional[int]
    user_type: bool
    nickname: Optional[str]
    user_phone: Optional[str]
    user_email: Optional[str]
    full_name: Optional[str]
    user_status: bool
    header_img: Optional[str]
    sex: int
