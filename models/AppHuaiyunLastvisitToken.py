'''
Created on 2014-6-16

@author: Administrator
'''

from mmstats.models import MongodbConn

class AppHuaiyunLastvisitToken(MongodbConn):
    
    def __init__(self, **kwargs):
        MongodbConn.__init__(self, **kwargs)
    
    


