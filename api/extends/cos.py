# -*- coding:utf-8 -*-
"""
@Time : 2022/6/9 10:21 AM
@Author: binkuolo
@Des: 腾讯云对象存储
"""
from core.Auth import check_permissions
from core.Response import success, fail
from sts.sts import Sts
from fastapi import APIRouter, Security, Request

from core.Utils import random_str
from models.base import SystemParams

router = APIRouter()


@router.get('/get/federation/token', dependencies=[Security(check_permissions)])
async def get_federation_token(req: Request, file_type: str):
    """
    获取临时访问token
    :return:
    """
    # 数据库写入配置参数
    # data = {
    #     "duration_seconds": 1800,
    #     "secret_id": '',
    #     "secret_key": "",
    #     "region": 'ap-chongqing'
    # }
    # await SystemParams.create(params_name="tencent_cos", params=data)
    # 临时访问密钥
    # qcloud-cos-sts-sdk https://github.com/tencentyun/qcloud-cos-sts-sdk/blob/master/python/demo/sts_demo.py
    result = await SystemParams.get_or_none(params_name="tencent_cos")
    file_path = 'fastapi/header-image/'
    if not result:
        return fail(msg="请配置腾讯云对象存储参数!")
    config = {
        'url': 'https://sts.tencentcloudapi.com/',
        # 域名，非必须，默认为 sts.tencentcloudapi.com
        'domain': 'sts.tencentcloudapi.com',
        # 临时密钥有效时长，单位是秒
        'duration_seconds': result.params.get("duration_seconds", None),
        'secret_id': result.params.get("secret_id", None),
        # 固定密钥
        'secret_key': result.params.get("secret_key", None),
        # 设置网络代理
        # 'proxy': {
        #     'http': 'xx',
        #     'https': 'xx'
        # },
        # 换成你的 bucket
        'bucket': 'fastapi-demo-1302232104',
        # 换成 bucket 所在地区
        'region': result.params.get("region", None),
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        # 'allow_prefix': f"fastapi/header-image/{req.state.user_id}.png",  # 固定文件名
        'allow_prefix': f"{file_path}*",  # 固定文件名
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 允许所有权限 不推荐
            # 'name/cos:*',
            # 检索存储桶操作权限
            # 'name/cos:HeadBucket',
            # 查询对象访问权限
            # 'name/cos:HeadObject',
            # 删除对象权限
            'name/cos:DeleteObject',
            # 查询查询存储桶跨域配置
            'name/cos:GetBucketCORS',
            # # 简单上传
            'name/cos:PutObject',
            # 获取对象   # 图片审核需要此权限
            'name/cos:GetObject',
            # 'name/cos:PostObject',
            # # 分片上传
            # 'name/cos:InitiateMultipartUpload',
            # 'name/cos:ListMultipartUploads',
            # 'name/cos:ListParts',
            # 'name/cos:UploadPart',
            # 'name/cos:CompleteMultipartUpload'
        ],
    }

    try:
        sts = Sts(config)
        response = sts.get_credential()
        data = dict(response)
        print(data)
        credentials: dict = data.get("credentials", None)
        if not credentials:
            return fail(msg="接口故障，请稍后再试!")
        res = {
            "TmpSecretId": credentials.get("tmpSecretId", None),
            "TmpSecretKey": credentials.get("tmpSecretKey", None),
            "SecurityToken": credentials.get("sessionToken", None),
            "StartTime": data.get("startTime", None),
            "ExpiredTime": data.get("expiredTime", None),
            "Bucket": config.get("bucket", None),
            "Region": config.get("region", None),
            "Key": f"{file_path}{random_str()}.{file_type}"
        }
        return success(msg="临时访问token", data=res)
    except Exception as e:
        print(e)
        return fail(msg="接口故障，请稍后再试!")

# 以下sdk demo 可以用在服务端做一些敏感操作的事情 exp: 创建存储桶 删除存储桶

# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
# from qcloud_cos import CosConfig
# from qcloud_cos import CosS3Client
# import sys
# import logging
#
# from config.cos import COS_SECRET_ID, COS_SECRET_KEY, COS_REGION, COS_TOKEN
#
# logging.basicConfig(level=logging.INFO, stream=sys.stdout)
#
# secret_id = COS_SECRET_ID      # 替换为用户的 secretId
# secret_key = COS_SECRET_KEY      # 替换为用户的 secretKey
# region = COS_REGION     # 替换为用户的 Region ap-chengdu
# token = COS_TOKEN                # 使用临时密钥需要传入 Token，默认为空，可不填
# scheme = 'https'            # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
# config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
#
# # 2. 获取客户端对象
# client = CosS3Client(config)
