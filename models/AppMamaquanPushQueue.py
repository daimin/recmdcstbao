'''
Created on 2014-6-16

@author: Administrator
'''

from mmstats.models import MongodbConn
import time

class AppMamaquanPushQueue(MongodbConn):
    
    def __init__(self, **kwargs):
        MongodbConn.__init__(self, **kwargs)
    
    def push(self, key, val):
        if not self._isexist(key):
            data = {}
            data.update(key)
            data['keystr'] = val
            data['t']      = time.time()
            self.insert(data)

    def pop(self, _type):
        item = self.find({"type":_type}).limit(1)

        if item.count() > 0:
            res_item = item[0]
            self.remove({"_id":res_item['_id']})
            return res_item
        else:
            return None
    





