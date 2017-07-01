#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

from myapp import db

# Create user model.
class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

# Create customer model.
class CustomerModel(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(20))
    mobile_tel = db.Column(db.String(11), unique=True)
    gender = db.Column(db.Integer)
    remark = db.Column(db.String(100))

    def __init__(self, user_id, name, mobile_tel, gender, remark):
        self.user_id = user_id
        self.name = name
        self.mobile_tel = mobile_tel
        self.gender = gender
        self.remark = remark

    def __repr__(self):
        return '<Customer %r>' % self.name

# Create company model.
class CompanyModel(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    tel = db.Column(db.String(20), unique=True)
    remark = db.Column(db.String(200))
    avatar = db.Column(db.String(255))

    def __init__(self, name, tel, remark, avatar):
        self.name = name
        self.tel = tel
        self.remark = remark
        self.avatar = avatar

    def __repr__(self):
        return '<Company %r>' % self.name

# Create company customer model.
class CompanyCustomerModel(db.Model):
    __tablename__ = 'company_customer'
    company_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, company_id, customer_id):
        self.company_id = company_id
        self.customer_id = customer_id
