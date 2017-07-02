#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

import os

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Dai253685_@10.5.216.83:3306/recmdcstbao?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = True

log_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "../logs"))

cache_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "../cache"))

## $platforms = array(1 => 'ios', 2 => 'android', 3 => 'qzone',4=>'web',5=>'ipad');
## 平台
PLATFORMS = {
             "IPhone"  :1,
             "Android" :2,
             "Ipad"    :5,
            }

TOKEN_KEYS = {
              "PUSH" : "*&&*PU_ke+S209H&*)()_",
              "KENG" : "cATG9Uk,@o6xf1Jw",
              "FMBK" : ".!@fM-----bK1{g]5=8&^)",
              "YWSB" : "*&&*PU_ke+S209H&*)()_"
              }

### ============ PUSH队列 ================ ###
PUSH_TYPE  = "push"
INTERFACE  = "http://test.push.mama.cn/device"
SECURE_KEY = "cATG9Uk,@o6xf1Jw"
