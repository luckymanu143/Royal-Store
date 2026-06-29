from flask import Flask, render_template, request, redirect, url_for, session

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.utils import secure_filename

from datetime import datetime

import razorpay

import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = 'royalstoresecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Rozopay

RAZORPAY_KEY_ID = "rzp_test_T5wtjQmI3Rue2E"
RAZORPAY_SECRET = "Cj84l0AXb1rQ5mOAa9X7l4vu"

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET)
)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ================= USER MODEL =================

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

# ================= PRODUCT MODEL =================

class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    price = db.Column(db.Integer, nullable=False)

    image = db.Column(db.String(200), nullable=False)

    category = db.Column(db.String(100))

    description = db.Column(db.Text)

# ================= ORDER MODEL =================

class Order(db.Model):

    __tablename__ = "order"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Customer

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    fullname = db.Column(
        db.String(150),
        nullable=False
    )

    mobile = db.Column(
        db.String(20),
        nullable=False
    )

    # Delivery Address

    address = db.Column(
        db.Text,
        nullable=False
    )

    city = db.Column(
        db.String(100),
        nullable=False
    )

    state = db.Column(
        db.String(100),
        nullable=False
    )

    pincode = db.Column(
        db.String(20),
        nullable=False
    )

    landmark = db.Column(
        db.String(200)
    )

    instructions = db.Column(
        db.Text
    )

    # Order Information

    total = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="Order Placed"
    )

    # Payment

    payment_method = db.Column(
        db.String(50),
        nullable=False
    )

    payment_status = db.Column(
        db.String(50),
        default="Pending"
    )

    payment_id = db.Column(
        db.String(200)
    )

    # Date

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ================= Add OrderItem Model =================

class OrderItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        nullable=False
    )

    product_name = db.Column(
        db.String(150),
        nullable=False
    )

    price = db.Column(
        db.Integer,
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )

# =============== Admin ================

@app.route('/admin')
@login_required
def admin():

    if not current_user.is_admin:
        return redirect(url_for('home'))

    products = Product.query.all()

    orders = Order.query.all()

    total_products = Product.query.count()

    total_orders = Order.query.count()

    total_users = User.query.count()

    return render_template(
        'admin.html',
        products=products,
        orders=orders,
        total_products=total_products,
        total_orders=total_orders,
        total_users=total_users
    )

# ============ Users =============

@app.route('/users')
@login_required
def users():

    if not current_user.is_admin:
        return redirect(url_for('home'))

    users = User.query.all()

    return render_template(
        'users.html',
        users=users
    )

# ============ Add Product Route ============

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():

    if not current_user.is_admin:
        return redirect(url_for('home'))

    if request.method == 'POST':

        print("Form Submitted")

        print(request.form)

        print(request.files)

        image = request.files['image']

        filename = secure_filename(image.filename)

        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        product = Product(
            name=request.form['name'],
            price=request.form['price'],
            image=filename,
            category=request.form['category'],
            description=request.form['description']
        )

        db.session.add(product)
        db.session.commit()

        print("Product Added Successfully")

        return redirect(url_for('admin'))

    return render_template('add_product.html')

# ============= Delete Product Route =============

@app.route('/delete_product/<int:id>')
@login_required
def delete_product(id):

    product = Product.query.get_or_404(id)

    db.session.delete(product)

    db.session.commit()

    return redirect('/admin')
# ============== Edit Product Route ===============

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):

    product = Product.query.get_or_404(id)

    if request.method == 'POST':

        product.name = request.form['name']

        product.price = request.form['price']

        product.category = request.form['category']

        product.description = request.form['description']

        image = request.files['image']

        if image.filename != "":

            filename = secure_filename(image.filename)

            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            product.image = filename

        db.session.commit()

        return redirect(url_for('admin'))

    return render_template(
        'edit_product.html',
        product=product
    )
# ============== Orders ================

@app.route('/orders')
@login_required
def orders():

    if not current_user.is_admin:
        return redirect(url_for('home'))

    orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template(
        'orders.html',
        orders=orders
    )

# ================ Update order ==============

@app.route('/update_order/<int:order_id>/<status>')
@login_required
def update_order(order_id, status):

    if not current_user.is_admin:
        return redirect(url_for('home'))

    order = Order.query.get_or_404(order_id)

    order.status = status

    db.session.commit()

    return redirect(url_for('orders'))

# ============ Add My Orders Route ===========

@app.route('/my_orders')
@login_required
def my_orders():

    orders = Order.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        'my_orders.html',
        orders=orders
    )

# ================= LOAD USER =================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= HOME ROUTE =================

@app.route('/')
def home():

    products = Product.query.all()

    return render_template('index.html', products=products)

# ================ Add Cart Route =================

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):

    product = Product.query.get(product_id)

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']

    cart.append({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'image': product.image
    })

    session['cart'] = cart

    return redirect(url_for('home'))

# ============= Cart Page Route =============

@app.route('/cart')
def cart():

    cart = session.get('cart', [])

    total = sum(item['price'] for item in cart)

    return render_template(
        'cart.html',
        cart=cart,
        total=total
    )

# ============== Remove Cart Item Route ===============

@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):

    cart = session.get('cart', [])

    if len(cart) > index:
        cart.pop(index)

    session['cart'] = cart

    return redirect(url_for('cart'))

# ================= ADDRESS =================
@app.route('/address', methods=['GET', 'POST'])
@login_required
def address():

    if request.method == 'POST':

        session['fullname'] = request.form['fullname']
        session['mobile'] = request.form['mobile']
        session['address'] = request.form['address']
        session['city'] = request.form['city']
        session['state'] = request.form['state']
        session['pincode'] = request.form['pincode']
        session['landmark'] = request.form.get('landmark', '')
        session['instructions'] = request.form.get('instructions', '')

        payment_method = request.form['payment_method']
        session['payment_method'] = payment_method

        if payment_method == "Online":
            return redirect(url_for('checkout'))

        elif payment_method == "COD":
            session["payment_status"] = "Pending"
            return redirect(url_for('success'))

    return render_template('address.html')

# ================= SUCCESS =================

@app.route('/success')
@login_required
def success():

    cart = session.get('cart', [])

    if not cart:
        return redirect(url_for('home'))

    total = sum(item['price'] for item in cart)

    order = Order(

        user_id=current_user.id,

        fullname=session.get('fullname'),

        mobile=session.get('mobile'),

        address=session.get('address'),

        city=session.get('city'),

        state=session.get('state'),

        pincode=session.get('pincode'),

        landmark=session.get('landmark'),

        instructions=session.get('instructions'),

        total=total,

        payment_method=session.get('payment_method'),

        payment_status="Paid"
        if session.get('payment_method') == "Online"
        else "Pending",

        payment_id=session.get('payment_id'),

        status="Order Placed"

    )

    db.session.add(order)

    db.session.commit()

    # Clear Cart
    session['cart'] = []

    # Clear Checkout Session Data
    session.pop('fullname', None)
    session.pop('mobile', None)
    session.pop('address', None)
    session.pop('city', None)
    session.pop('state', None)
    session.pop('pincode', None)
    session.pop('landmark', None)
    session.pop('instructions', None)
    session.pop('payment_method', None)
    session.pop('payment_id', None)

    return render_template(
        'success.html',
        order=order
    )

# ================= CHECKOUT =================

@app.route('/checkout')
@login_required
def checkout():

    cart = session.get('cart', [])

    if not cart:
        return redirect(url_for('cart'))

    total = sum(item['price'] for item in cart)

    # Save total in session
    session['total'] = total

    try:

        payment = client.order.create({

            "amount": total * 100,      # Amount in paise

            "currency": "INR",

            "payment_capture": 1

        })

        return render_template(

            "checkout.html",

            cart=cart,

            total=total,

            payment=payment,

            razorpay_key=RAZORPAY_KEY_ID

        )

    except Exception as e:

        print("Razorpay Error:", e)

        return f"Razorpay Error: {str(e)}"

# ================= REGISTER =================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# ============== Search ==================

@app.route('/search')
def search():

    query = request.args.get('query')

    products = Product.query.filter(
        Product.name.contains(query)
    ).all()

    return render_template(
        'search.html',
        products=products
    )

# ============== Product Details page ================

@app.route('/product/<int:id>')
def product_detail(id):

    product = Product.query.get_or_404(id)

    return render_template(
        'product_detail.html',
        product=product
    )

# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            if user.is_admin:
                return redirect(url_for('admin'))

            return redirect(url_for('home'))

    return render_template('login.html')

# ================= LOGOUT =================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('home'))

# ================= RUN APP =================

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)