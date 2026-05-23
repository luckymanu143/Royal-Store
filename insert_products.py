from app import app, db, Product

with app.app_context():

    # Product 1
    product1 = Product(
        name="Black Oversized T-Shirt",
        price=799,
        image="tshirt1.jpg"
    )

    # Product 2
    product2 = Product(
        name="Sports Shorts",
        price=599,
        image="shorts1.jpg"
    )

    # Product 3
    product3 = Product(
        name="Premium Track Pants",
        price=1199,
        image="trackpant1.jpg"
    )

    # Product 4
    product4 = Product(
        name="Royal Hoodie",
        price=1499,
        image="hoodie1.jpg"
    )

    # Add products to database
    db.session.add(product1)
    db.session.add(product2)
    db.session.add(product3)
    db.session.add(product4)

    # Save changes
    db.session.commit()

    print("Products Added Successfully")