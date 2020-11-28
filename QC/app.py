from flask.signals import request_finished
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from flask import Flask, render_template, redirect, url_for, request, flash, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, downgrade
from sqlalchemy.sql.schema import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/bmp-qc"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


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

    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

    def __repr__(self):
        return f"<Name {self.name}>"


class ProductsModel(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    bmpid = db.Column(db.Integer(), unique=True)
    desc = db.Column(db.String())
    customer = db.Column(db.String(), ForeignKey("customers.customer"))
    lastqc = db.Column(db.DateTime())
    requirements = db.Column(db.JSON())

    def __init__(self, bmpid, desc, customer, lastqc, requirements):
        self.bmpid = bmpid
        self.desc = desc
        self.customer = customer
        self.lastqc = lastqc
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

'''
 ______________
< Login System >
 --------------
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
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = UserModel.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('index'))

@app.route('/signup')
# @login_required
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
# @login_required
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = UserModel.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = UserModel(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return UserModel.query.get(int(user_id))


'''
 _________________
< Web Application >
 -----------------
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
# Home Page + Profile Page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)



# Product Pages
@app.route('/products', methods=['POST', 'GET'])
@login_required
def handle_products():
    customers = CustomersModel.query.all()
    customerResults = [
        {
            "id" : customer.id,
            "customer": customer.customer
        } for customer in customers]
    if request.method == 'POST':
        bmpid = int(request.form.get("bmpid"))
        desc = request.form.get("desc")
        customer = request.form.get("customer")
        lastqc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        requirements = request.form.get("requirements")
        if not requirements:
            requirements = "{\"None\" : \"N/A\"}"
        requirements = json.loads(requirements)

        new_product = ProductsModel(bmpid, desc, customer, lastqc, requirements)
        if not check_product_exists(new_product):
            db.session.add(new_product)
            db.session.commit()
            products = ProductsModel.query.all()
            results = [
                {
                    "id" : product.id,
                    "bmpid": product.bmpid,
                    "desc": product.desc,
                    "customer": product.customer,
                    "lastqc": product.lastqc,
                    "requirements": product.requirements
                } for product in products]
            return render_template('products.html', results=results, customerResults=customerResults, status_good=f"Success! Product: '{new_product.desc} | {new_product.bmpid}' has been created.")
        else:
            products = ProductsModel.query.all()
            results = [
                {
                    "id" : product.id,
                    "bmpid": product.bmpid,
                    "desc": product.desc,
                    "customer": product.customer,
                    "lastqc": product.lastqc,
                    "requirements": product.requirements
                } for product in products]
            return render_template('products.html', results=results, customerResults=customerResults, status_bad=f"Fail...  BMP Product ID: '{new_product.bmpid}' already exists.")

    elif request.method == 'GET':
        products = ProductsModel.query.all()
        results = [
            {
                "id" : product.id,
                "bmpid": product.bmpid,
                "desc": product.desc,
                "customer": product.customer,
                "lastqc": product.lastqc,
                "requirements": product.requirements
            } for product in products]
        if len(results) == 0:
            return render_template('products.html', customerResults=customerResults, no_products="No Products to Display")
        else:
            return render_template('products.html', results=results, customerResults=customerResults)

@app.route('/products/<product_id>', methods=['GET', 'POST', 'DELETE'])
def handle_product(product_id):
    product = ProductsModel.query.get_or_404(product_id)

    if request.method == 'GET':
        response = {
            "id" : product.id,
            "bmpid": product.bmpid,
            "desc": product.desc,
            "customer": product.customer,
            "lastqc": product.lastqc,
            "requirements": product.requirements
        }
        return {"message": "success", "product": response}

    elif request.method == 'POST':
        # This will update the product in the product table.
        # If editing the BMP ID, then the QC table will need to be updated as well.
        flash("OK")
        return{"POST": "POST THINGY"}

    elif request.method == 'DELETE':
        qcRecords = ProductsModel.query.filter_by(id=product_id).first() #change this once qc table built
        if (qcRecords): #change this to not qcRecords once QC table is built
            db.session.delete(product)
            db.session.commit()
            flash("Product successfully deleted.")
            return {"Success": "Product has been deleted."}
        else:
            flash("Product unable to be deleted since it has QC records tied to it.")
            return {"Success": "Product not deleted."}



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
            customers = CustomersModel.query.all()
            results = [
                {
                    "id" : customer.id,
                    "customer": customer.customer
                } for customer in customers]
            return render_template('customers.html', results=results, status_good=f"Success! Customer: '{new_customer.customer} | {new_customer.id}' has been created.")
        else:
            customers = CustomersModel.query.all()
            results = [
                {
                    "id" : customer.id,
                    "customer": customer.customer
                } for customer in customers]
            return render_template('customers.html', results=results, status_bad=f"Fail...  Customer: '{new_customer.customer}' already exists.")

    elif request.method == 'GET':
        customers = CustomersModel.query.all()
        results = [
            {
                "id" : customer.id,
                "customer": customer.customer
            } for customer in customers]
        if len(results) == 0:
            return render_template('customers.html', no_customers="No Customers to Display")
        else:
            return render_template('customers.html', results=results)

@app.route('/customers/<customer_id>', methods=['GET', 'POST', 'DELETE'])
def handle_customer(customer_id):
    customer = CustomersModel.query.get_or_404(customer_id)
    customer_name = customer.customer

    if request.method == 'GET':
        response = {
            "id" : customer.id,
            "customer": customer.customer
        }
        return {"message": "success", "customer": response}

    elif request.method == 'POST':
        # This will update the customer name in the customers table.
        # Only works if customer name doesn't exist.
        # Update entries in product and qc tables.
        flash("OK")
        return{"POST": "POST THINGY"}

    elif request.method == 'DELETE':
        # qcRecords = QCModel.query.filter_by(customer=customer_name).first() #change this once qc table built
        productRecords = ProductsModel.query.filter_by(customer=customer_name).first()
        print(productRecords)
        if (productRecords == None): #change this to not qcRecords once QC table is built
            db.session.delete(customer)
            db.session.commit()
            flash("Customer successfully deleted.")
            return {"Success": "Customer has been deleted."}
        else:
            flash("Customer unable to be deleted since it has Product or QC records tied to it.")
            return {"Success": "Customer not deleted."}

'''
 _____
< API >
 -----
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
@app.route('/api')
def api_home():
    return {"Hello" : "World"}


@app.route('/api/products', methods=['GET', 'POST'])
def handle_products_api():
    if request.method == 'GET':
        products = ProductsModel.query.all()
        results = [
            {
                "id" : product.id,
                "bmpid": product.bmpid,
                "desc": product.desc,
                "customer": product.customer,
                "lastqc": product.lastqc,
                "requirements": product.requirements
            } for product in products]
        return {"count": len(results), "products": results, "message": "success"}
    elif request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            lastqc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            requirements = data['requirements']
            if not requirements:
                requirements = "{\"None\" : \"N/A\"}"
            new_product = ProductsModel(bmpid=data['bmpid'], desc=data['desc'], customer=data['customer'], lastqc=lastqc, requirements=requirements)
            if not check_product_exists(new_product):
                db.session.add(new_product)
                db.session.commit()
                return {"Success": f"Product: '{new_product.desc} | {new_product.bmpid}' has been created."}
            else:
                return {"Fail": f"BMP Product ID: '{new_product.bmpid}' already exists."}
        else:
            return {"API Error": "The request payload is not in JSON format"}


@app.route('/api/products/<product_id>', methods=['GET', 'POST', 'DELETE'])
def handle_product_api(product_id):
    product = ProductsModel.query.get_or_404(product_id)

    if request.method == 'GET':
        response = {
            "id" : product.id,
            "bmpid": product.bmpid,
            "desc": product.desc,
            "customer": product.customer,
            "lastqc": product.lastqc,
            "requirements": product.requirements
        }
        return {"message": "success", "product": response}

    elif request.method == 'POST':
        data = request.get_json()
        exists = False
        if (product.bmpid != data['bmpid']):
            exists = False
            products = ProductsModel.query.all()
            for product in products:
                if (product.bmpid == data['bmpid']):
                    exists = True

        if exists:
            exists = False
            return {"Fail": f"Product not updated. BMP Product ID '{product.bmpid}' already exists."}
        else:
            product.bmpid = data['bmpid']
            product.desc = data['desc']
            product.customer = data['customer']
            product.lastqc = data['lastqc']
            product.requirements = data ['requirements']
            db.session.add(product)
            db.session.commit()
            return {"Success": f"Product: '{product.desc} | {product.bmpid}' has been updated."}

    elif request.method == 'DELETE':
        qcRecords = ProductsModel.query.filter_by(id=product_id).first() #change this once qc table built
        if (qcRecords): #change this to not qcRecords once QC table is built
            db.session.delete(product)
            db.session.commit()
            return {"Success": f"Product: '{product.desc} | {product.bmpid}' successfully deleted."}
        else:
            return {"Fail": f"Product: '{product.desc} | {product.bmpid}' unable to be deleted since it has QC records tied to it."}


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


if __name__ == '__main__':
    app.run(debug=True)