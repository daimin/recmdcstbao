#!/usr/bin/env python
# -*- coding:utf-8 -*-   
#encoding=utf-8
#author=daimin

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')
app.config.from_object('myapp.conf')

db = SQLAlchemy(app)

from models import UserModel
from views import *