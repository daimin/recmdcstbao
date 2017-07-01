#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

from myapp import app
from myapp import lib

class Customer():
    @app.route('/api/customer/save', methods=['POST'])
    def save(self):
        return lib.params.response_std([])

customer = Customer()
customer.init_app(app)