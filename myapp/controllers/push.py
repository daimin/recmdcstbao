#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
"""
push系统专用接口
"""
from flask import request, json
from myapp import comm
from myapp import lib
from myapp import conf
from myapp import app

import math
import time
import os
import sys

logger = comm.getlogger("%s.log" %  __file__, ap=True)

@app.route('/test', methods=['GET',])
def test(): 
    return lib.params.response_std([]) 
            



