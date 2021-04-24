from flask_login import login_required
from flask import render_template, request, flash
from models import *
from config import *
from functions import *

# Customer Pages
@app.route('/customers', methods=['POST', 'GET'])
@login_required
def handle_customers():
    if request.method == 'POST':
        customer = request.form.get("customer")

        new_customer = CustomersModel(customer)
        if not check_customer_exists(new_customer):
            db.session.add(new_customer)
            db.session.commit()
            results = query_customers()
            return render_template('customers.html', results=results, status_good=f"Success! Customer: '{new_customer.customer} | {new_customer.id}' has been created.")
        else:
            results = query_customers()
            return render_template('customers.html', results=results, status_bad=f"Fail...  Customer: '{new_customer.customer}' already exists.")

    elif request.method == 'GET':
        results = query_customers()
        if len(results) == 0:
            return render_template('customers.html', no_customers="No Customers to Display")
        else:
            return render_template('customers.html', results=results)

@app.route('/customers/<customer_id>', methods=['GET', 'POST', 'DELETE'])
def handle_customer(customer_id):
    customer = CustomersModel.query.get_or_404(customer_id)
    customer_info = query_customer_info(customer_id)
    productResults = query_customer_products(customer_id)
    logResults = query_customer_logs(customer_id)
    if request.method == 'GET':
        if len(productResults) == 0:
            return render_template('customer.html', customer_info=customer_info, no_products="No Products to Display", no_logs="No QC Logs to Display")
        elif len(logResults) == 0:
            return render_template('customer.html', customer_info=customer_info, productResults=productResults, no_logs="No QC Logs to Display")
        else:
            return render_template('customer.html', customer_info=customer_info, productResults=productResults, logResults=logResults)

    elif request.method == 'POST':
        new_customer_name = request.form.get('customer')
        if new_customer_name != customer.customer:
            customer.customer = new_customer_name
            db.session.commit()
        customer_info = query_customer_info(customer_id)
        productResults = query_customer_products(customer_id)
        logResults = query_customer_logs(customer_id)
        if len(productResults) == 0:
            return render_template('customer.html', customer_info=customer_info, no_products="No Products to Display", no_logs="No QC Logs to Display")
        elif len(logResults) == 0:
            return render_template('customer.html', customer_info=customer_info, productResults=productResults, no_logs="No QC Logs to Display")
        else:
            return render_template('customer.html', customer_info=customer_info, productResults=productResults, logResults=logResults)

    elif request.method == 'DELETE':
        customer_name = customer.customer
        productRecord = ProductsModel.query.filter_by(customer=customer_name).first()
        if (productRecord == None):
            db.session.delete(customer)
            db.session.commit()
            flash("Customer successfully deleted.")
            return {"Success": "Customer has been deleted."}
        else:
            flash("Customer unable to be deleted since it has Products tied to it.")
            return {"Success": "Customer not deleted."}