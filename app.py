from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from datetime import datetime

import razorpay
import os

# =====================================================
# Flask Configuration
# =====================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "royalstoresecret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Av%40271104@127.0.0.1:3306/bundle_store'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = "static/images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# =====================================================
# Razorpay
# =====================================================

RAZORPAY_KEY_ID = "rzp_test_T5wtjQmI3Rue2E"

RAZORPAY_SECRET = "Cj84l0AXb1rQ5mOAa9X7l4vu"

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET)
)

# =====================================================
# Login Manager
# =====================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

# =====================================================
# User Model
# =====================================================

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False
    )

# =====================================================
# Product Model
# =====================================================

class Product(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    price = db.Column(
        db.Integer,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    image = db.Column(
        db.String(200),
        nullable=False
    )

# =====================================================
# Wishlist Model
# =====================================================

class Wishlist(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id")
    )

    product = db.relationship(
        "Product"
    )

# =====================================================
# Order Model
# =====================================================

class Order(db.Model):

    __tablename__ = "order"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    fullname = db.Column(
        db.String(150),
        nullable=False
    )

    mobile = db.Column(
        db.String(20),
        nullable=False
    )

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

    total = db.Column(
        db.Integer,
        nullable=False
    )

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

    status = db.Column(
        db.String(50),
        default="Order Placed"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="orders"
    )

# =====================================================
# Order Item Model
# =====================================================

class OrderItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id")
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

    order = db.relationship(
        "Order",
        backref="items"
    )

# =====================================================
# Flask Login
# =====================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =====================================================
# Home
# =====================================================

@app.route("/")
def home():

    products = Product.query.all()

    return render_template(
        "index.html",
        products=products
    )


# =====================================================
# Register
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing = User.query.filter_by(email=email).first()

        if existing:

            flash("Email already registered.", "danger")

            return redirect(url_for("register"))

        user = User(

            username=username,

            email=email,

            password=generate_password_hash(password)

        )

        db.session.add(user)

        db.session.commit()

        flash("Registration Successful. Please Login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# =====================================================
# Login
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            if user.is_admin:

                return redirect(url_for("admin"))

            return redirect(url_for("home"))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")


# =====================================================
# Logout
# =====================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("home"))


# =====================================================
# Search
# =====================================================

@app.route("/search")
def search():

    keyword = request.args.get("query", "")

    products = Product.query.filter(
        Product.name.ilike(f"%{keyword}%")
    ).all()

    return render_template(
        "search.html",
        products=products
    )


# =====================================================
# Product Details
# =====================================================

@app.route("/product/<int:id>")
def product_detail(id):

    product = Product.query.get_or_404(id)

    related_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(4).all()

    return render_template(

        "product_detail.html",

        product=product,

        products=related_products

    )

# =====================================================
# Add To Cart
# =====================================================

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    product = Product.query.get_or_404(product_id)

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]

    found = False

    for item in cart:
        if item["id"] == product.id:
            item["quantity"] += 1
            found = True
            break

    if not found:
        cart.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "image": product.image,
            "quantity": 1
        })

    session["cart"] = cart

    flash("Product added to cart.", "success")

    return redirect(request.referrer or url_for("home"))


# =====================================================
# Cart
# =====================================================

@app.route("/cart")
def cart():

    cart = session.get("cart", [])

    total = sum(item["price"] * item["quantity"] for item in cart)

    return render_template(
        "cart.html",
        cart=cart,
        total=total
    )


# =====================================================
# Remove From Cart
# =====================================================

@app.route("/remove_from_cart/<int:index>")
def remove_from_cart(index):

    cart = session.get("cart", [])

    if 0 <= index < len(cart):
        cart.pop(index)

    session["cart"] = cart

    flash("Item removed from cart.", "info")

    return redirect(url_for("cart"))


# =====================================================
# Wishlist
# =====================================================

@app.route("/wishlist")
@login_required
def wishlist():

    wishlist = Wishlist.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "wishlist.html",
        wishlist=wishlist
    )


# =====================================================
# Add To Wishlist
# =====================================================

@app.route("/add_to_wishlist/<int:product_id>")
@login_required
def add_to_wishlist(product_id):

    exists = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if not exists:

        item = Wishlist(
            user_id=current_user.id,
            product_id=product_id
        )

        db.session.add(item)
        db.session.commit()

        flash("Added to wishlist.", "success")

    return redirect(request.referrer or url_for("home"))


# =====================================================
# Remove Wishlist
# =====================================================

@app.route("/remove_wishlist/<int:product_id>")
@login_required
def remove_wishlist(product_id):

    item = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if item:

        db.session.delete(item)
        db.session.commit()

        flash("Removed from wishlist.", "info")

    return redirect(url_for("wishlist"))


# =====================================================
# Address
# =====================================================

@app.route("/address", methods=["GET", "POST"])
@login_required
def address():

    if request.method == "POST":

        session["fullname"] = request.form["fullname"]
        session["mobile"] = request.form["mobile"]
        session["address"] = request.form["address"]
        session["city"] = request.form["city"]
        session["state"] = request.form["state"]
        session["pincode"] = request.form["pincode"]
        session["landmark"] = request.form.get("landmark", "")
        session["instructions"] = request.form.get("instructions", "")

        payment_method = request.form["payment_method"]

        session["payment_method"] = payment_method

        # ONLINE PAYMENT
        if payment_method == "Online":
            return redirect(url_for("checkout"))

        # CASH ON DELIVERY
        elif payment_method == "COD":
            session["payment_status"] = "Pending"
            session["payment_id"] = None

            return redirect(url_for("success"))

        flash("Please select a valid payment method.", "danger")
        return redirect(url_for("address"))

    return render_template("address.html")


# =====================================================
# Checkout
# =====================================================

@app.route("/checkout")
@login_required
def checkout():

    cart = session.get("cart", [])

    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart"))

    total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    payment = client.order.create({

        "amount": total * 100,

        "currency": "INR",

        "payment_capture": 1

    })

    session["total"] = total

    return render_template(

        "checkout.html",

        cart=cart,

        total=total,

        payment=payment,

        razorpay_key=RAZORPAY_KEY_ID

    )

# =====================================================
# Success / Place Order
# =====================================================

@app.route("/success")
@login_required
def success():

    # Get cart
    cart = session.get("cart", [])

    # If cart is empty, go back to home
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("home"))

    # Calculate total
    total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    # Get payment method
    payment_method = session.get("payment_method")

    # Safety check
    if not payment_method:
        flash("Please select a payment method.", "warning")
        return redirect(url_for("address"))

    # =================================================
    # PAYMENT STATUS
    # =================================================

    if payment_method == "COD":
        payment_status = "Pending"
        payment_id = None

    elif payment_method == "Online":
        payment_status = "Paid"
        payment_id = request.args.get("razorpay_payment_id")

    else:
        payment_status = "Pending"
        payment_id = None

    # =================================================
    # CREATE ORDER
    # =================================================

    order = Order(

        user_id=current_user.id,

        fullname=session.get("fullname"),

        mobile=session.get("mobile"),

        address=session.get("address"),

        city=session.get("city"),

        state=session.get("state"),

        pincode=session.get("pincode"),

        landmark=session.get("landmark"),

        instructions=session.get("instructions"),

        total=total,

        payment_method=payment_method,

        payment_status=payment_status,

        payment_id=payment_id,

        status="Order Placed"

    )

    # Save order
    db.session.add(order)

    db.session.commit()

    # =================================================
    # SAVE ORDER ITEMS
    # =================================================

    for item in cart:

        order_item = OrderItem(

            order_id=order.id,

            product_name=item["name"],

            price=item["price"],

            quantity=item["quantity"]

        )

        db.session.add(order_item)

    db.session.commit()

    # =================================================
    # CLEAR CART
    # =================================================

    session.pop("cart", None)

    # =================================================
    # CLEAR CHECKOUT DATA
    # =================================================

    session.pop("fullname", None)
    session.pop("mobile", None)
    session.pop("address", None)
    session.pop("city", None)
    session.pop("state", None)
    session.pop("pincode", None)
    session.pop("landmark", None)
    session.pop("instructions", None)
    session.pop("payment_method", None)
    session.pop("payment_status", None)
    session.pop("payment_id", None)
    session.pop("total", None)

    # =================================================
    # SUCCESS MESSAGE
    # =================================================

    if payment_method == "COD":

        flash(
            "Order placed successfully! Pay cash when your order is delivered.",
            "success"
        )

    else:

        flash(
            "Order placed successfully!",
            "success"
        )

    # =================================================
    # SUCCESS PAGE
    # =================================================

    return render_template(
        "success.html",
        order=order
    )

# =====================================================
# My Orders
# =====================================================

@app.route("/my_orders")
@login_required
def my_orders():

    orders = Order.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Order.created_at.desc()

    ).all()

    return render_template(

        "my_orders.html",

        orders=orders

    )

# =====================================================
# Admin Dashboard
# =====================================================

@app.route("/admin")
@login_required
def admin():

    if not current_user.is_admin:
        return redirect(url_for("home"))

    products = Product.query.all()

    total_products = Product.query.count()
    total_users = User.query.count()
    total_orders = Order.query.count()

    recent_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(10).all()

    return render_template(
        "admin.html",
        products=products,
        orders=recent_orders,
        total_products=total_products,
        total_users=total_users,
        total_orders=total_orders
    )


# =====================================================
# Users
# =====================================================

@app.route("/users")
@login_required
def users():

    if not current_user.is_admin:
        return redirect(url_for("home"))

    users = User.query.all()

    return render_template(
        "users.html",
        users=users
    )


# =====================================================
# Delete User
# =====================================================

@app.route("/delete_user/<int:id>")
@login_required
def delete_user(id):

    if not current_user.is_admin:
        return redirect(url_for("home"))

    user = User.query.get_or_404(id)

    if user.is_admin:
        flash("Admin account cannot be deleted.", "danger")
        return redirect(url_for("users"))

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully.", "success")

    return redirect(url_for("users"))


# =====================================================
# Add Product
# =====================================================

@app.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():

    if not current_user.is_admin:
        return redirect(url_for("home"))

    if request.method == "POST":

        image = request.files["image"]

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        product = Product(
            name=request.form["name"],
            category=request.form["category"],
            price=int(request.form["price"]),
            description=request.form["description"],
            image=filename
        )

        db.session.add(product)
        db.session.commit()

        flash("Product added successfully.", "success")

        return redirect(url_for("admin"))

    return render_template("add_product.html")


# =====================================================
# Edit Product
# =====================================================

@app.route("/edit_product/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product(id):

    if not current_user.is_admin:
        return redirect(url_for("home"))

    product = Product.query.get_or_404(id)

    if request.method == "POST":

        product.name = request.form["name"]
        product.category = request.form["category"]
        product.price = int(request.form["price"])
        product.description = request.form["description"]

        image = request.files.get("image")

        if image and image.filename:

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            product.image = filename

        db.session.commit()

        flash("Product updated successfully.", "success")

        return redirect(url_for("admin"))

    return render_template(
        "edit_product.html",
        product=product
    )


# =====================================================
# Delete Product
# =====================================================

@app.route("/delete_product/<int:id>")
@login_required
def delete_product(id):

    if not current_user.is_admin:
        return redirect(url_for("home"))

    product = Product.query.get_or_404(id)

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully.", "success")

    return redirect(url_for("admin"))


# =====================================================
# Orders
# =====================================================

@app.route("/orders")
@login_required
def orders():

    if not current_user.is_admin:
        return redirect(url_for("home"))

    orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "orders.html",
        orders=orders
    )


# =====================================================
# Update Order Status
# =====================================================

@app.route("/update_order/<int:id>", methods=["POST"])
@login_required
def update_order(id):

    if not current_user.is_admin:
        return redirect(url_for("home"))

    order = Order.query.get_or_404(id)

    order.status = request.form["status"]

    db.session.commit()

    flash("Order updated successfully.", "success")

    return redirect(url_for("orders"))


# =====================================================
# Run Application
# =====================================================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )

