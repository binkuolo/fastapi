# -*- coding:utf-8 -*-
"""
@Time : 2022/4/23 7:47 PM
@Author: binkuolo
@Des: 登陆测试
"""
from typing import List
from pydantic import BaseModel


class Login(BaseModel):
    username: str
    password: str
    user: List[int]


def index(age: int = 80):
    return {"fun": "/index", "age": age}


def login(data: Login):
    return data
