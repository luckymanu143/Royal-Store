from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():

    admin = User(
        username="admin",
        email="admin@bundle.com",
        password=generate_password_hash("Admin@123"),
        is_admin=True
    )

    db.session.add(admin)
    db.session.commit()

    print("Admin created successfully")