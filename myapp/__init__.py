#!/usr/bin/env python
# -*- coding:utf-8 -*-   
#encoding=utf-8
#author=daimin

from flask import Flask
app = Flask(__name__, template_folder='templates')
app.config.from_object('myapp.conf')

from controllers import *