# -*- coding:utf-8 -*-
"""
@Time : 2022/6/9 10:21 AM
@Author: binkuolo
@Des: 腾讯云对象存储
"""

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
