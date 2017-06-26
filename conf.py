#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

import os

mongodb = {
    "write" :{
        #"host"   : "119.145.147.180",
        "host"   : "192.168.18.181",
        "port"   : 27017,
        "user"   : "xloguser",
        "passwd" : "^__^123456xlog*@*",
        "db"     : "xlog_debug",
        "bulk_size" : 1000,
        "batch_size": 10240,
    },
    "read" : {
        "port" : 27017,
    }
}

redis = {
        "host" : "192.168.18.181",
        "port" : 6379,
        "db"   : 5,
        }


log_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "logs"))

cache_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "cache"))

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
