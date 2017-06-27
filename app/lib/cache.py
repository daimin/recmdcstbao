#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
"""缓存
"""
import conf, comm
import datetime
import time
import os
from flask import json


logger = comm.getlogger("%s.log" % __file__, ap=True)

INVALID_TIME = 7200  # 失效时间默认是2小时

def get_cache_key(params, is_hash=True):
    #keyhour = datetime.datetime.now().strftime("%Y-%m-%d-%H")
    if is_hash:
        return "%s" % (comm.md5(str(params)))
    else:
        return "%s" % (str(params))

def __remove_invalid_cache():
    """删除无用的缓存文件
    """
    cachedir = get_cache_dir()
    for cachefile in os.listdir(cachedir):
        if cachefile.startswith("__"): ## 指定前缀的文件不于删除，由其它系统维护
            continue
        cachefile = os.path.join(cachedir, cachefile)
        if os.stat(cachefile).st_mtime + INVALID_TIME < time.time():
            logger.info("Remove file %s" % cachefile)
            os.remove(cachefile)

def read(key, invalid_time=None):
    cachefile = os.path.join(get_cache_dir(), key)
    if not os.path.exists(cachefile):
        return None

    invalid_time = INVALID_TIME if invalid_time is None else invalid_time
    ## 检查生效时间，失效时间为修改时间 + 过期时间
    if os.stat(cachefile).st_mtime + invalid_time < time.time():
        os.remove(cachefile)
        return None
    __remove_invalid_cache()
    
    with open(cachefile) as cachef:
        try:
            return json.loads(cachef.read())
        except Exception, e:
            print e
            return None
        
    return None

def get_cache_dir():
    cpath = os.path.join(conf.cache_dir, datetime.datetime.today().strftime("%Y%m%d"))
    if not os.path.exists(cpath):
        os.mkdir(cpath)
    return cpath

def write(key, val):
    cachefile = os.path.join(get_cache_dir(), key)
    with open(cachefile, "w") as cachef:
        cachef.write(json.dumps(val))
        
    
    
