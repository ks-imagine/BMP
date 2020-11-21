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
        return f"<Product {self.name}>"


class ProductsModel(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    model = db.Column(db.String(), unique=True)
    client = db.Column(db.String())
    weight = db.Column(db.Integer())

    def __init__(self, name, model, client, weight):
        self.name = name
        self.model = model
        self.client = client
        self.weight = weight

    def __repr__(self):
        return f"<Product {self.name}>"


def check_product_exists(_product):
    exists = False
    products = ProductsModel.query.all()
    for product in products:
        if (product.model == _product.model):
            exists = True
    return exists




# main.py
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)



# auth.py
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
@login_required
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



#### Application
@app.route('/products', methods=['POST', 'GET'])
@login_required
def handle_products():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_product = ProductsModel(name=data['name'], model=data['model'], client=data['client'], weight=data['weight'])

            if not check_product_exists(new_product):
                db.session.add(new_product)
                db.session.commit()
                return {"message": f"Product {new_product.name} has been created successfully."}
            else:
                return {"message": f"Product '{new_product.name}' already exists."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        products = ProductsModel.query.all()
        results = [
            {
                "name": product.name,
                "model": product.model,
                "client": product.client,
                "weight": product.weight
            } for product in products]

        return render_template('products.html', name=current_user.name, results=results)


@app.route('/products/<product_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def handle_product(product_id):
    product = ProductsModel.query.get_or_404(product_id)

    if request.method == 'GET':
        response = {
            "name": product.name,
            "model": product.model,
            "client": product.client,
            "weight": product.weight
        }
        return {"message": "success", "product": response}

    elif request.method == 'PUT':
        data = request.get_json()
        exists = False
        if (product.model != data['model']):
            exists = False
            products = ProductsModel.query.all()
            for product in products:
                if (product.model == data['model']):
                    exists = True

        if exists:
            exists = False
            return {"message": f"product {product.name} not updated. model: {product.model} already exists."}
        else:
            product.name = data['name']
            product.model = data['model']
            product.client = data['client']
            product.weight = data['weight']
            db.session.add(product)
            db.session.commit()
            return {"message": f"product {product.name} successfully updated"}

    elif request.method == 'DELETE':
        db.session.delete(product)
        db.session.commit()

        return {"message": f"Product {product.name} successfully deleted."}


### API
@app.route('/api/products', methods=['GET'])
def handle_products_api():
    if request.method == 'GET':
        products = ProductsModel.query.all()
        results = [
            {
                "name": product.name,
                "model": product.model,
                "client": product.client,
                "weight": product.weight
            } for product in products]
        return {"count": len(results), "products": results, "message": "success"}



if __name__ == '__main__':
    app.run(debug=True)