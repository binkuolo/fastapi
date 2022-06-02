# -*- coding:utf-8 -*-
"""
@Time : 2022/5/4 10:54 PM
@Author: binkuolo
@Des: 基础schemas
"""
from pydantic import BaseModel, Field
from typing import List, Any, Optional


class BaseResp(BaseModel):
    code: int = Field(description="状态码")
    message: str = Field(description="信息")
    data: List = Field(description="数据")


class ResAntTable(BaseModel):
    success: bool = Field(description="状态码")
    data: List = Field(description="数据")
    total: int = Field(description="总条数")


class WebsocketMessage(BaseModel):
    action: Optional[str]
    user: Optional[int]
    data: Optional[Any]
