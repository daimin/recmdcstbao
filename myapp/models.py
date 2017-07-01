#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

from myapp import db

# Create user model.
class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    mobile_tel = db.Column(db.String(11), unique=True)
    password = db.Column(db.String(32))

    def __repr__(self):
        return '<User %r>' % self.mobile_tel

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    # Required for administrative interface
    def __unicode__(self):
        return self.mobile_tel

# Create customer model.
class CustomerModel(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    mobile_tel = db.Column(db.String(11), unique=True)
    gender = db.Column(db.Integer)
    remark = db.Column(db.String(100))

    def __init__(self, name, mobile_tel, gender, remark):


