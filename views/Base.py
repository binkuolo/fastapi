# -*- coding:utf-8 -*-
"""
@Time : 2022/4/23 11:46 AM
@Author: binkuolo
@Des: 视图路由
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse


from views.home import home

ViewsRouter = APIRouter()


ViewsRouter.get("/", tags=["门户首页"], response_class=HTMLResponse)(home)
