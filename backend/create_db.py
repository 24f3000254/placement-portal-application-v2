from app import app, db
from models import User

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email="admin@gmail.com").first()

    if admin is None:
        admin = User(
            name="Admin",
            email="admin@gmail.com",
            password="admin",
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("admin user created successfully.")

    print("database created successfully.")