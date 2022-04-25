# -*- coding:utf-8 -*-
"""
@Created on : 2022/4/22 22:02
@Author: binkuolo
@Des: 基本路由
"""
from fastapi import APIRouter

from api.login import index, login
from api.test_redis import test_my_redis, test_my_redis_depends

ApiRouter = APIRouter(prefix="/v1", tags=["api路由"])

ApiRouter.get("/index", tags=["api路由"], summary="注册接口")(index)

ApiRouter.post("/login", tags=["api路由"], summary="登陆接口")(login)

ApiRouter.get("/test/my/redis", tags=["api路由"], summary="fastapi的state方式")(test_my_redis)

ApiRouter.get("/test/my/redis/depends", tags=["api路由"], summary="依赖注入方式")(test_my_redis_depends)


