#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
"""
push系统专用接口
"""
from flask import request
import comm
import lib
import conf

import math
from flask import json
import time
import os
import sys
import controllers

logger = comm.getlogger("%s.log" %  __file__, ap=True)


@controllers.app.route('/test', methods=['GET',])
def test(): 
    return lib.params.response_std([]) 
            



