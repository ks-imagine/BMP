from flask_login import login_required
from flask import render_template, request, flash, json
from models import *
from config import *
from functions import *

# Product Pages
@app.route('/products', methods=['POST', 'GET'])
@login_required
def handle_products():
    customerResults = query_customers()
    if request.method == 'POST':
        bmpid = int(request.form.get("bmpid"))
        description = request.form.get("description")
        customer = request.form.get("customer")
        requirements = request.form.get("requirements")
        if not requirements:
            requirements = "{\"None\" : \"N/A\"}"
        requirements = json.loads(requirements)

        new_product = ProductsModel(bmpid, description, customer, requirements)
        if not check_product_exists(new_product):
            db.session.add(new_product)
            db.session.commit()
            results = query_products()
            return render_template('products.html', results=results, customerResults=customerResults, status_good=f"Success! Product: '{new_product.description} | {new_product.bmpid}' has been created.")
        else:
            results = query_products()
            return render_template('products.html', results=results, customerResults=customerResults, status_bad=f"Fail...  BMP Product ID: '{new_product.bmpid}' already exists.")

    elif request.method == 'GET':
        results = query_products()
        if len(results) == 0:
            return render_template('products.html', customerResults=customerResults, no_products="No Products to Display")
        else:
            return render_template('products.html', results=results, customerResults=customerResults)

@app.route('/products/<product_id>', methods=['GET', 'POST', 'DELETE'])
def handle_product(product_id):
    product = ProductsModel.query.get_or_404(product_id)
    bmpid = product.bmpid
    response = {
            "id" : product.id,
            "bmpid": product.bmpid,
            "description": product.description,
            "customer": product.customer,
            "requirements": product.requirements
        }

    if request.method == 'GET':
        return {"message": "success", "product": response}

    elif request.method == 'POST':
        # This will update the product in the product table.
        # If editing the BMP ID, then the QC table will need to be updated as well.
        flash("OK")
        return{"POST": "POST THINGY"}

    elif request.method == 'DELETE':
        qcRecord = LogsModel.query.filter_by(bmpid=bmpid).first()
        if (qcRecord == None):
            db.session.delete(product)
            db.session.commit()
            flash("Product successfully deleted.")
            return {"Success": "Product has been deleted."}
        else:
            flash("Product unable to be deleted since it has QC records tied to it.")
            return {"Success": "Product not deleted."}

