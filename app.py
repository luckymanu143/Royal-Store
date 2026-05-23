from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Product Model
class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    price = db.Column(db.Integer, nullable=False)

    image = db.Column(db.String(200), nullable=False)

# Home Route
@app.route('/')
def home():

    products = Product.query.all()

    return render_template('index.html', products=products)

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)