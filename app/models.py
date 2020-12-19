from flask_login import UserMixin
from sqlalchemy.sql.schema import ForeignKey
from config import *

'''
 ___________
< DB Models >
 -----------
   \
    \
     \
        __ \ / __
       /  \ | /  \
           \|/
       _.---v---.,_
      /            \  /\__/\
     /              \ \_  _/
     |__ @           |_/ /
      _/                /
      \       \__,     /
   ~~~~\~~~~~~~~~~~~~~`~~~
'''
class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

    def __repr__(self):
        return f"<Name {self.name}>"


class LogsModel(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    bmpid = db.Column(db.Integer(), ForeignKey("products.bmpid"))
    lastqc = db.Column(db.DateTime())
    user = db.Column(db.String())
    requirements = db.Column(db.JSON())

    def __init__(self, bmpid, lastqc, user, requirements):
        self.bmpid = bmpid
        self.lastqc = lastqc
        self.user = user
        self.requirements = requirements

    def __repr__(self):
        return f"<Log {self.id}>"


class ProductsModel(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    bmpid = db.Column(db.Integer(), unique=True)
    description = db.Column(db.String())
    customer = db.Column(db.String(), ForeignKey("customers.customer"))
    requirements = db.Column(db.JSON())

    def __init__(self, bmpid, description, customer, requirements):
        self.bmpid = bmpid
        self.description = description
        self.customer = customer
        self.requirements = requirements

    def __repr__(self):
        return f"<Product {self.bmpid}>"


class CustomersModel(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(), unique=True)

    def __init__(self, customer):
        self.customer = customer

    def __repr__(self):
        return f"<Customer {self.customer}>"
