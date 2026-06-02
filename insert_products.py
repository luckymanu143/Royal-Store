from app import app, db, Product

with app.app_context():

    products = [

        Product(
            name="Black Oversized T-Shirt",
            price=799,
            image="tshirt1.jpg",
            category="T-Shirts",
            description="Premium oversized cotton t-shirt with comfortable fit."
        ),

        Product(
            name="Sports Shorts",
            price=599,
            image="shorts1.jpg",
            category="Shorts",
            description="Lightweight sports shorts suitable for gym and outdoor activities."
        ),

        Product(
            name="Premium Track Pants",
            price=1199,
            image="trackpant1.jpg",
            category="Track Pants",
            description="Premium quality track pants designed for comfort and style."
        ),

        Product(
            name="Royal Hoodie",
            price=1499,
            image="hoodie1.jpg",
            category="Hoodies",
            description="Luxury hoodie made with soft cotton fabric."
        )

    ]

    db.session.add_all(products)

    db.session.commit()

    print("Products inserted successfully!")