from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from connect_database import db_connector
import mysql.connector
import marshmallow_sqlalchemy
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Luna2794@localhost/e_Commerce'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15))
    orders = db.relationship('order', backref='customer')

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))

class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('customer', backref='Customer_account', uselist=False)

order_product = db.Table('Order_Product',
    db.Column('order_id',db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
)


class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', secondary=order_product, backref=db.backref('products'))

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "id")

class ProductSchema(ma.Schema):
    name = fields.String(required=True)
    price = fields.Float(required=True)

class AccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Integer(required=True)

class OrderSchema(ma.Schema):
    date = fields.Date(required=True)
    customer_id = fields.Integer(required=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

#------Customer-----------------------------------------------------------------------------------------------

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_info = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_info['name'], email=customer_info['email'], phone=customer_info['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "Customer added"}), 201


@app.route('/customers/<int:id>', methods = ['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_info = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer.name = customer_info['name']
    customer.email = customer_info['email']
    customer.phone = customer_info['phone']
    db.session.commit()
    return jsonify({"message": "Customer updated"}), 200


@app.route('/customers/<int:id>', methods = ['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted"}), 200


@app.route('/customers', methods = ['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

#-----------Customer Account---------------------------------------------------

@app.route('/customer_accounts', methods = ['POST'])
def add_account():
    try:
        account_info = account_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_account = CustomerAccount(username=account_info['username'], password=account_info['password'], customer_id=account_info['customer_id'])
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "Account added"}), 201


@app.route('/customer_accounts', methods = ['GET'])
def get_accounts():
    accounts = CustomerAccount.query.all()
    return accounts_schema.jsonify(accounts)


@app.route('/customer_accounts/<int:id>', methods = ['PUT'])
def update_account(id):
    account = CustomerAccount.query.get_or_404(id)
    try:
        account_info = account_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    account.username = account_info['username']
    account.password = account_info['password']
    account.customer_id = account_info['customer_id']
    db.session.commit()
    return jsonify({"message": "Account updated"}), 200


@app.route('/customer_accounts/<int:id>', methods = ['DELETE'])
def delete_account(id):
    account = CustomerAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Account deleted"}), 200



#----------Product-----------------------------------------------------------------------

@app.route('/products', methods = ["POST"])
def add_product():
    try:
        product_info = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(name=product_info['name'], price=product_info['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added"}), 201


@app.route('/products/<int:id>', methods = ['GET'])
def get_one_product(id):
    product = Product.query.get_or_404(id)
    return product_schema.jsonify(product)


@app.route('/products/<int:id>', methods = ['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_info = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.name = product_info['name']
    product.price = product_info['price']
    db.session.commit()
    return jsonify({"message": "Product updated"}), 200


@app.route('/products/<int:id>', methods = ['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200


@app.route('/products', methods = ['GET'])
def get_all_products():
    products = Product.query.all()
    return accounts_schema.jsonify(products)


#------------Orders-------------------------------------------------------------------------

@app.route('/orders', methods = ["POST"])
def place_order():
    try:
        order_info = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Order(date=order_info['date'], order_product=order_info['order_product'], customer_id=order_info['customer_id'])
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "Order placed"}), 201


@app.route('/orders/<int:id>', methods = ['GET'])
def get_order(id):
    order = Order.query.get_or_404(id)
    return order_schema.jsonify(order)


@app.route('/order_product/<int:id>', methods = ['GET'])
def track_order(id):
    order = Order.query.get_or_404(id)
    return order_schema.jsonify(order)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)



