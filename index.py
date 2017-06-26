#!/usr/bin/env python
# -*- coding:utf-8 -*-   
#encoding=utf-8
#author=daimin
from flask import Flask
app = Flask(__name__, template_folder='templates')

from controllers import *

app.debug = True
app.secret_key = 'Acdb56432fdsghfcb&8743'


app.run(host='0.0.0.0', debug=True)


