from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from flask import Flask, render_template, Blueprint, redirect, url_for, request, flash, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import sys


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
    customer = db.Column(db.String())
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

@app.route('/products', methods=['POST', 'GET'])
@login_required
def handle_products():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_product = ProductsModel(bmpid=data['bmpid'], desc=data['desc'], customer=data['customer'], lastqc=data['lastqc'], requirements=data['requirements'])

            if not check_product_exists(new_product):
                db.session.add(new_product)
                db.session.commit()
                return {"Success": f"Product: '{new_product.desc} | {new_product.bmpid}' has been created."}
            else:
                return {"Fail": f"BMP Product ID: '{new_product.bmpid}' already exists."}
        else:
            return {"Error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        products = ProductsModel.query.all()
        results = [
            {
                "bmpid": product.bmpid,
                "desc": product.desc,
                "customer": product.customer,
                "lastqc": product.lastqc,
                "requirements": product.requirements
            } for product in products]
        if len(results) == 0:
            return render_template('products.html', no_products="No Products to Display")
        else:
            return render_template('products.html', results=results)


@app.route('/products/<product_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_product(product_id):
    product = ProductsModel.query.get_or_404(product_id)

    if request.method == 'GET':
        response = {
            "bmpid": product.bmpid,
            "desc": product.desc,
            "customer": product.customer,
            "lastqc": product.lastqc,
            "requirements": product.requirements
        }
        return {"message": "success", "product": response}

    elif request.method == 'PUT':
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
        db.session.delete(product)
        db.session.commit()

        return {"Success": f"Product: '{product.desc} | {product.bmpid}' has been deleted."}


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
            new_product = ProductsModel(bmpid=data['bmpid'], desc=data['desc'], customer=data['customer'], lastqc=data['lastqc'], requirements=data['requirements'])
            if not check_product_exists(new_product):
                db.session.add(new_product)
                db.session.commit()
                return {"Success": f"Product: '{new_product.desc} | {new_product.bmpid}' has been created."}
            else:
                return {"Fail": f"BMP Product ID: '{new_product.bmpid}' already exists."}
        else:
            return {"Error": "The request payload is not in JSON format"}



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


if __name__ == '__main__':
    app.run(debug=True)