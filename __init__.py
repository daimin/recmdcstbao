#!/usr/bin/env python
# -*- coding:utf-8 -*-   
#encoding=utf-8
#author=daimin

from flask import Flask

app = Flask(__name__, template_folder='templates')

app.debug = True
app.secret_key = 'Acdb56432fdsghfcb&8743'

@app.route('/')
def index():
    return 'Sorry!<br/>&nbsp;&nbsp;Please do not direct access to the interface.'

from controllers import *
