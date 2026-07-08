from flask import Flask
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

# Connect SQLAlchemy to Flask
db.init_app(app)

with app.app_context():

    # Create all tables
    db.create_all()

    # Check whether admin exists
    admin = User.query.filter_by(email="admin@trekverse.com").first()

    if not admin:

        admin = User(
            name="Administrator",
            email="admin@trekverse.com",
            password="admin123",
            phone="9999999999",
            role="admin",
            approved=True,
            blacklisted=False
        )

        db.session.add(admin)
        db.session.commit()

        print(" Default Admin Created")

    else:
        print(" Admin Already Exists")


@app.route("/")
def home():
    return "Welcome to TrekVerse - Trekking Management Application"


if __name__ == "__main__":
    app.run(debug=True)