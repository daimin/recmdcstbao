#!/usr/bin/env python
# -*- coding:utf-8 -*-   
#encoding=utf-8
#author=daimin

import requests

"""
网络处理类
这里使用requests库实现
"""
class NetHandler:
    
    __handler = None
    
    def __init__(self):
        self.__headers = {'content-type': 'application/json'}

    @staticmethod
    def get_instance():
        NetHandler.__handler = NetHandler() if NetHandler.__handler is None else NetHandler.__handler
        return NetHandler.__handler
    
    def __res_json(self, res):
        res.encoding = 'utf-8'
        return res.text if  res.status_code == requests.codes.ok else None
    
    def get(self, url, **kwargs):
        res = None
        try:
            res = requests.get(url, headers = self.__headers, params = kwargs)
            return self.__res_json(res)
        except:
            return None
        
        return None
    
    def post(self, url, **kwargs):   
        #kwargs['headers'] = self.__headers
        res = None
        try:
            res = requests.post(url, **kwargs)
            return self.__res_json(res)
        except:
            return None
        
        
def get(url, **kwargs):
    return NetHandler.get_instance().get(url, **kwargs)

def post(url, **kwargs):
    return NetHandler.get_instance().post(url, **kwargs)


if __name__ == "__main__":
    print post("http://www.baidu.com", data={"t":21312321}, timeout=0.01)
