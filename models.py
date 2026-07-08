from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ==========================
# USER TABLE
# ==========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(15))

    role = db.Column(db.String(20), nullable=False)
    # admin / staff / user

    approved = db.Column(db.Boolean, default=False)

    blacklisted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    managed_treks = db.relationship(
        "Trek",
        backref="staff",
        lazy=True
    )

    bookings = db.relationship(
        "Booking",
        backref="user",
        lazy=True
    )


# ==========================
# TREK TABLE
# ==========================
class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    duration = db.Column(db.Integer, nullable=False)

    available_slots = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String(20), default="Pending")
    # Pending/Open/Closed/Completed

    start_date = db.Column(db.Date)

    end_date = db.Column(db.Date)

    description = db.Column(db.Text)

    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    bookings = db.relationship(
        "Booking",
        backref="trek",
        lazy=True
    )


# ==========================
# BOOKING TABLE
# ==========================
class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    booking_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(20),
        default="Booked"
    )
    # Booked/Cancelled/Completed

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id"),
        nullable=False
    )