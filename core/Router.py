# -*- coding:utf-8 -*-
"""
@Time : 2022/4/23 11:43 AM
@Author: binkuolo
@Des: 路由聚合
"""
from api.api import api_router
from views.views import views_router
from fastapi import APIRouter


router = APIRouter()
# 视图路由
router.include_router(views_router)
# API路由
router.include_router(api_router)

