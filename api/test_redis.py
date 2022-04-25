# -*- coding:utf-8 -*-
"""
@Time : 2022/4/25 2:37 PM
@Author: binkuolo
@Des: test redis
"""

from core.Response import success
from fastapi import Depends, Request
from database.redis import sys_cache
from aioredis import Redis


async def test_my_redis(req: Request):
    # 连接池放在request
    value = await req.app.state.cache.get("today")

    return success(msg="test_my_redis", data=[value])


async def test_my_redis_depends(today: int, cache: Redis = Depends(sys_cache)):
    # 连接池放在依赖注入
    # await cache.set(name="today", value=today)
    await cache.set(name="ex_today", value=today, ex=60)
    # value = await cache.get("today")
    return success(msg=f"今天是{today}号", data=[])
