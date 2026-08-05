from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():

    db.drop_all()
    db.create_all()

    admin = User.query.filter_by(email="admin@gmail.com").first()

    if admin is None:

        admin = User(
            name="Admin",
            email="admin@gmail.com",
            password=generate_password_hash("admin"),
            role="admin",
            approved=True,
            active=True
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin Created")

    print("Database Created")