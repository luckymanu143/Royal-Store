from flask import session
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

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

# ================= PRODUCT MODEL =================

class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    price = db.Column(db.Integer, nullable=False)

    image = db.Column(db.String(200), nullable=False)

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