from flask import session
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'royalstoresecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

# ================= Add Order Model =================

class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    total = db.Column(db.Integer, nullable=False)

    status = db.Column(
        db.String(50),
        default="Order Placed"
    )

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
# ============ Add Product Route ============

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():

    if request.method == 'POST':

        product = Product(

            name=request.form['name'],

            price=request.form['price'],

            image=request.form['image'],

            category=request.form['category'],

            description=request.form['description']

        )

        db.session.add(product)

        db.session.commit()

        return redirect('/admin')

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

        product.image = request.form['image']

        product.category = request.form['category']

        product.description = request.form['description']

        db.session.commit()

        return redirect('/admin')

    return render_template(
        'edit_product.html',
        product=product
    )

# ================= RUN APP =================

@app.route('/success')
@login_required
def success():

    cart = session.get('cart', [])

    total = sum(item['price'] for item in cart)

    order = Order(
        user_id=current_user.id,
        total=total,
        status="Order Placed"
    )

    db.session.add(order)

    db.session.commit()

    session['cart'] = []

    return render_template('success.html')

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

    return redirect(url_for('cart'))

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

# =========== Create Checkout Route ============

@app.route('/checkout')
@login_required
def checkout():

    cart = session.get('cart', [])

    total = sum(item['price'] for item in cart)

    return render_template(
        'checkout.html',
        cart=cart,
        total=total
    )

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