"""
Created on 2015-3-10

@author: daimin
"""

from mmstats.models import MongodbConn

class UpdateQueueStat(MongodbConn):
    def __init__(self, **kwargs):
        MongodbConn.__init__(self, **kwargs)

