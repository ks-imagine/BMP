from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from flask import Flask, render_template, redirect, url_for, request, flash, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql.schema import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import desc


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


# QC Pages
@app.route('/logs', methods=['POST', 'GET'])
@login_required
def handle_logs():
    productResults = query_products()
    if request.method == 'POST':
        bmpid = int(request.form.get("bmpid"))
        lastqc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = current_user.name
        requirements = request.form.get("requirements")
        if not requirements:
            requirements = "{\"None\" : \"N/A\"}"
        requirements = json.loads(requirements)

        new_log = LogsModel(bmpid, lastqc, user, requirements)
        db.session.add(new_log)
        db.session.commit()
        results = query_logs()
        return render_template('logs.html', results=results, productResults=productResults, status_good=f"Success! Log: '{new_log.id}' has been created.")
    elif request.method == 'GET':
        results = query_logs()
        if len(results) == 0:
            return render_template('logs.html', productResults=productResults, no_logs="No Logs to Display")
        else:
            return render_template('logs.html', productResults=productResults, results=results)

@app.route('/logs/<log_id>', methods=['GET', 'POST', 'DELETE'])
def handle_log(log_id):
    log = LogsModel.query.get_or_404(log_id)
    response = {
            "id" : log.id,
            "bmpid": log.bmpid,
            "lastqc": log.lastqc,
            "user" : log.user,
            "requirements": log.requirements
        }
    if request.method == 'GET':
        return {"message": "success", "product": response}

    elif request.method == 'POST':
        # This will update the product in the product table.
        # If editing the BMP ID, then the QC table will need to be updated as well.
        flash("OK")
        return{"POST": "POST THINGY"}

    elif request.method == 'DELETE':
        logDate = LogsModel.query.filter_by(id=log_id).first()
        if (logDate.lastqc > (datetime.now() - timedelta(days=2))):
            db.session.delete(log)
            db.session.commit()
            flash("QC Log successfully deleted.")
            return {"Success": "QC Log has been deleted."}
        else:
            flash("QC Log unable to be deleted since it was entered over 24 hours ago.")
            return {"Success": "QC Log not deleted."}


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
        qcRecords = LogsModel.query.filter_by(bmpid=bmpid).first() #change this once qc table built
        if (qcRecords == None): #change this to not qcRecords once QC table is built
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
    customer_name = customer.customer
    customer_info = {
            "id" : customer.id,
            "customer": customer.customer
        }
    productRecords = ProductsModel.query.filter_by(customer=customer_name)
    productResults = [
        {
        "id" : product.id,
        "bmpid": product.bmpid,
        "description": product.description,
        "customer": product.customer,
        "requirements": product.requirements
        } for product in productRecords]
    logRecords = LogsModel.query.filter_by(bmpid=12345) #Edit this.. Learn to serach by foreign key
    logResults = [
        {
        "id": log.id,
        "bmpid" : log.bmpid,
        "lastqc" : log.lastqc,
        "user" : log.user
        } for log in logRecords]
    if request.method == 'GET':
        if len(productResults) == 0:
            return render_template('customer.html', customer_info=customer_info, no_products="No Products to Display", no_logs="No QC Logs to Display")
        elif len(logResults) == 0:
            return render_template('customer.html', customer_info=customer_info, productResults=productResults, no_logs="No QC Logs to Display")
        else:
            return render_template('customer.html', customer_info=customer_info, productResults=productResults, logResults=logResults)

    elif request.method == 'POST':
        # This will update the customer name in the customers table.
        # Only works if customer name doesn't exist.
        # Update entries in product and qc tables.
        flash("OK")
        return{"POST": "POST THINGY"}

    elif request.method == 'DELETE':
        if (productRecords == None):
            db.session.delete(customer)
            db.session.commit()
            flash("Customer successfully deleted.")
            return {"Success": "Customer has been deleted."}
        else:
            flash("Customer unable to be deleted since it has Products tied to it.")
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

# Removed API Logic on 11/28/2020 @ 9:52pm ET


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

if __name__ == '__main__':
    app.run(debug=True)