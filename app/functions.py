from sqlalchemy import desc
from models import *
from config import *

'''
 __________________
< Random Functions >
 ------------------
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
def check_product_exists(_product):
    exists = False
    products = ProductsModel.query.all()
    for product in products:
        if (product.bmpid == _product.bmpid):
            exists = True
    return exists

def check_customer_exists(_customer):
    exists = False
    customers = CustomersModel.query.all()
    for customer in customers:
        if (customer.customer == _customer.customer):
            exists = True
    return exists

def query_logs():
    logs = db.session.query(LogsModel.id, LogsModel.bmpid, LogsModel.lastqc, LogsModel.user, LogsModel.requirements, ProductsModel.description, ProductsModel.customer).join(ProductsModel).order_by(desc('lastqc'))
    results = [
        {
            "id" : log.id,
            "bmpid": log.bmpid,
            "lastqc": log.lastqc,
            "user" : log.user,
            "requirements": log.requirements,
            "description": log.description,
            "customer": log.customer
        } for log in logs]
    return results

def query_products():
    products = ProductsModel.query.order_by(desc('bmpid'))
    results = [
        {
            "id" : product.id,
            "bmpid": product.bmpid,
            "description": product.description,
            "customer": product.customer,
            "requirements": product.requirements
        } for product in products]
    return results

def query_customers():
    customers = CustomersModel.query.all()
    results = [
        {
            "id" : customer.id,
            "customer": customer.customer
        } for customer in customers]
    return results

def query_customer_info(customer_id):
    customer = CustomersModel.query.get_or_404(customer_id)
    customer_info = {
        "id" : customer.id,
        "customer": customer.customer
    }
    return customer_info
def query_customer_products(customer_id):
    customer = CustomersModel.query.get_or_404(customer_id)
    customer_name = customer.customer
    productRecords = ProductsModel.query.filter_by(customer=customer_name)
    productResults = [
        {
        "id" : product.id,
        "bmpid": product.bmpid,
        "description": product.description,
        "customer": product.customer,
        "requirements": product.requirements
        } for product in productRecords]
    return productResults
def query_customer_logs(customer_id):
    logRecords = LogsModel.query.filter_by(bmpid=12345) #Edit this.. Learn to serach by foreign key
    logResults = [
        {
        "id": log.id,
        "bmpid" : log.bmpid,
        "lastqc" : log.lastqc,
        "user" : log.user
        } for log in logRecords]
    return logResults


### THESE ARE DOG SHIT DELETE THEM AND BURN YOUR EYES OUT ###
def query_requirements():
    products = ProductsModel.query.order_by(desc('bmpid'))
    parsedRequirements = [
    {
        "id" : requirement.id,
        "reqs" : parse_requirements(requirement.requirements)
    } for requirement in products]
    return parsedRequirements

def parse_requirements(requirement):
    reqLength = len(requirement["reqs"])
    parsedRequirement = ""
    while reqLength > 0:
        parsedRequirement += "Description (Short): " + requirement["reqs"][reqLength - 1]["s-req"] + " Description (Long): " + requirement["reqs"][reqLength - 1]["l-req"] + " Value Type: " + requirement["reqs"][reqLength - 1]["v-typ"] + " Maximum Value: " + requirement["reqs"][reqLength - 1]["max"] + " Minimum Value: " + requirement["reqs"][reqLength - 1]["min"]
        reqLength -= 1
    return parsedRequirement
### END DOG SHIT ###
