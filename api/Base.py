# -*- coding:utf-8 -*-
"""
@Created on : 2022/4/22 22:02
@Author: binkuolo
@Des: 基本路由
"""
from fastapi import APIRouter

from api.login import index, login

ApiRouter = APIRouter(prefix="/v1", tags=["api路由"])


@ApiRouter.get('/input')
async def home(num: int):
    return {"num": num, "data": [{"num": num, "data": []}, {"num": num, "data": []}]}

ApiRouter.get("/index", tags=["api路由"], summary="注册接口")(index)

ApiRouter.post("/login", tags=["api路由"], summary="登陆接口")(login)

