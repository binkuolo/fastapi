# -*- coding:utf-8 -*-
"""
@Created on : 2022/4/22 22:02
@Author: binkuolo
@Des: 基本路由
"""
from fastapi import APIRouter
router = APIRouter()


@router.get('/')
async def home(num: int):

    return num
