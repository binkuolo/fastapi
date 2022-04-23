# -*- coding:utf-8 -*-
"""
@Time : 2022/4/23 11:43 AM
@Author: binkuolo
@Des: 路由聚合
"""
from api.Base import ApiRouter
from views.Base import ViewsRouter
from fastapi import APIRouter


AllRouter = APIRouter()
# 视图路由
AllRouter.include_router(ViewsRouter)
# API路由
AllRouter.include_router(ApiRouter)

