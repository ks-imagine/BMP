from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/bmp-qc-api"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class ProductsModel(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    model = db.Column(db.String(), unique=True)
    weight = db.Column(db.Integer())

    def __init__(self, name, model, weight):
        self.name = name
        self.model = model
        self.weight = weight

    def __repr__(self):
        return f"<Product {self.name}>"


class UsersModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    employeeid = db.Column(db.Integer())

    def __init__(self, name, model, weight):
        self.name = name
        self.email = email
        self.employeeid = employeeid

    def __repr__(self):
        return f"<User {self.name}>"


def check_product_exists(_product):
    exists = False
    products = ProductsModel.query.all()
    for product in products:
        if (product.model == _product.model):
            exists = True
    return exists


@app.route('/')
def main():
	return {"hello": "world"}


@app.route('/products', methods=['POST', 'GET'])
def handle_products():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_product = ProductsModel(name=data['name'], model=data['model'], weight=data['weight'])

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
                "weight": product.weight
            } for product in products]

        return {"count": len(results), "products": results, "message": "success"}


@app.route('/products/<product_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_product(product_id):
    product = ProductsModel.query.get_or_404(product_id)

    if request.method == 'GET':
        response = {
            "name": product.name,
            "model": product.model,
            "weight": product.weight
        }
        return {"message": "success", "product": response}

    elif request.method == 'PUT':
        data = request.get_json()
        product.name = data['name']
        product.model = data['model']
        product.weight = data['weight']

        db.session.add(product)
        db.session.commit()

        return {"message": f"product {product.name} successfully updated"}

    elif request.method == 'DELETE':
        db.session.delete(product)
        db.session.commit()

        return {"message": f"Product {product.name} successfully deleted."}


if __name__ == '__main__':
    app.run(debug=True)