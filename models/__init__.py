#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

import mmstats
import pymongo
import redis 
from mmstats import conf
from mmstats import comm
from pymongo.errors import BulkWriteError
from pymongo.errors import DuplicateKeyError


logger = comm.getlogger("db.log", ap=True)


class RedisConn(object):
    """Redis处理基类
    """
    __pool     = None
    
    def __init__(self, **kwargs):
        if RedisConn.__pool is None:
            RedisConn.__pool = redis.ConnectionPool(host=kwargs.get("host"), port=kwargs.get("port"), db=kwargs.get("db"))
        self.__dbconn = redis.Redis(connection_pool=RedisConn.__pool)
        self.__dbconn.ping()

        self.pipeline = self.__dbconn.pipeline()
       
    def get(self, key):
        return self.__dbconn.get(key)
        
    def set(self, key, val, expire=0):
        self.__dbconn.set(key, val, expire)
        
    def llen(self, key):
        return self.__dbconn.llen(key)

    def rpush(self, key, v):
        return self.__dbconn.rpush(key ,v)

    def lpush(self, key, v):
        return self.__dbconn.lpush(key ,v)

    def lpop(self, key):
        return self.__dbconn.lpop(key)

    def lrange(self, key, l, r):
        return self.__dbconn.lrange(key, l, r)

    def _del(self, keys):
        if isinstance(keys, list):
            keys = tuple(keys)
        return self.__dbconn.delete(keys)

    def hsetnx(self, key, field, value):
        return self.__dbconn.hsetnx(key, field, value)

    def close(self):
        if hasattr(self.__dbconn, "close"):
            return self.__dbconn.close()


    @staticmethod
    def getinstance():
        return RedisConn(**conf.redis)
 

class MongodbConn(object):
    """mongodb连接对象
    """
    instances = {}
    
    def __init__(self, **kwargs):
        self.__dbconfig = kwargs
        self._readconn, self._writeconn, self_readdb, self._writedb = None, None, None, None
        ## 处理mongodb的读写配置
        if "read" not in self.__dbconfig:
            self.__dbconfig['read'] = {}

        for k,v in self.__dbconfig['write'].iteritems():
            if k not in self.__dbconfig['read']:
                self.__dbconfig['read'][k] = v

        self.__reconnect()
        self.__bulk_size  = kwargs.get("bulk_size", 1)
        self.__update_cnt = 0
        self.__bulk = None
        self.__is_support_bulk = False


        
    def __reconnect(self):

        for _t, dbcfg in self.__dbconfig.iteritems():
            if _t not in ('read', 'write'): continue  ## 只有read和write才是数据库配置
            conn_name = "_%sconn" % _t
            conn_obj  = getattr(self, conn_name)
            if conn_obj is None or conn_obj.alive() == False:
                conn_obj = pymongo.MongoClient(dbcfg['host'], dbcfg['port'])
                logger.warning("Connect to [%s] db: %s.%s" % (_t, dbcfg['db'], self.__dbconfig['tab']))
                db_obj   = conn_obj["%s" % dbcfg['db']]
                setattr(self, conn_name, conn_obj)
                setattr(self, "_%sdb"  % _t, db_obj)
                setattr(self, "_%stab" % _t, db_obj[self.__dbconfig['tab']])

    
    def insert(self, data, intime=False):
        if intime or self.__is_support_bulk == False:
            try:
                return self._writetab.insert(data, continue_on_error=True)
            except DuplicateKeyError,e:
                logger.error(e)
                return None

        if self.__bulk is None:
            self.init_bulk()
        self.__bulk.insert(data)
        self.__update_cnt += 1
        if self.__update_cnt >= self.__bulk_size:
             self.execute_bulk()

    def init_bulk(self):
        if not self.__is_support_bulk:
            raise Exception("Not support bulk op!")
        self.__bulk = self._writetab.initialize_unordered_bulk_op()
        self.__update_cnt = 0

    def execute_bulk(self):
        if not self.__is_support_bulk:
            raise Exception("Not support bulk op!")
        try:
            self.__bulk.execute()
        except BulkWriteError as bwe:
            logger.warning(bwe.details)
            print bwe.details
            
        self.init_bulk()
        
    def update(self, where, data, intime=False):
        if intime or self.__is_support_bulk == False:
            if "$inc" in data or "$set" in data or "$addToSet" in data or "$push" in data:
                return self._writetab.update(where, data)
            else:
                return self._writetab.update(where, {"$set" : data})

        if self.__bulk is None:
            self.init_bulk()
        self.__bulk.find(where).update(data)
        self.__update_cnt += 1
        if self.__update_cnt >= self.__bulk_size:
             self.execute_bulk()

    def replace_one(self, where, data):
        if not self.__is_support_bulk:
            raise Exception("Not support bulk op!")
        if self.__bulk is None:
            self.init_bulk()
        self.__bulk.find(where).replace_one(data)
        self.__update_cnt += 1
        if self.__update_cnt >= self.__bulk_size:
             self.execute_bulk()
        
    def update_one(self, where, data):
        if not self.__is_support_bulk:
            self.update(where, data)
        else:
            if self.__bulk is None:
                self.init_bulk()
            #where = {"uid" : "13580006"}
            self.__bulk.find(where).update_one({"$set": data})
            self.__update_cnt += 1
            if self.__update_cnt >= self.__bulk_size:
                 self.execute_bulk()
        
    def drop(self):
        self._writetab.drop()
        
    def remove(self, data):
        return self._writetab.remove(data)
    
    def find_one(self, where):
        return self._readtab.find_one(where)
    
    def find(self, where, field=None): 
        if field is None:
            return self._readtab.find(where)
        else:
            return self._readtab.find(where, field)

    def _isexist(self, key):
        if self.find_one(key):
            return True
        return False
    
    @property
    def writetab(self):
        return self._writetab

    @property
    def readtab(self):
        return self._readtab


    def __del__(self):
        self._readdb.close()
        self._readconn.close()
        self._writedb.close()
        self._writeconn.close()

    @classmethod
    def getinstance(cls, options=None):
        clzname = cls.__name__
        if clzname not in cls.instances:
            ## 修改类名方式以适应mongoengine
            conf.mongodb['tab'] = "".join(map(lambda x:"_" + x.lower() if x.isupper() else x.lower(), clzname)).strip("_")
            cls.instances[clzname] = cls(**conf.mongodb)
        else:
            cls.instances[clzname].__reconnect()  
            
        return cls.instances[clzname]
