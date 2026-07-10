from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import datetime

from models import db, User, Trek, Booking


def register_routes(app):

    # ----------------------------
    # Home Page
    # ----------------------------
    @app.route("/")
    def home():
        return render_template("home.html")


    # ----------------------------
    # Register
    # ----------------------------
    @app.route("/register", methods=["GET", "POST"])
    def register():

        if request.method == "POST":

            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            password = request.form["password"]
            role = request.form["role"]

            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                return "Email already registered."

            # Staff needs admin approval
            approved = True if role == "user" else False

            user = User(
                name=name,
                email=email,
                phone=phone,
                password=generate_password_hash(password),
                role=role,
                approved=approved
            )

            db.session.add(user)
            db.session.commit()

            return redirect(url_for("login"))

        return render_template("register.html")


    # ----------------------------
    # Login
    # ----------------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():

        if request.method == "POST":

            email = request.form["email"]
            password = request.form["password"]

            user = User.query.filter_by(email=email).first()

            if not user:
                return "User not found"

            if not check_password_hash(user.password, password):
                return "Incorrect password"

            if user.blacklisted:
                return "Account Blacklisted"

            if user.role == "staff" and not user.approved:
                return "Waiting for Admin Approval"

            session["user_id"] = user.id
            session["role"] = user.role
            session["name"] = user.name

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            elif user.role == "staff":
                return redirect(url_for("staff_dashboard"))

            else:
                return redirect(url_for("user_dashboard"))

        return render_template("login.html")


    # ----------------------------
    # Logout
    # ----------------------------
    @app.route("/logout")
    def logout():

        session.clear()

        return redirect(url_for("home"))


    # ----------------------------
    # Admin Dashboard
    # ----------------------------
    @app.route("/admin/dashboard")
    def admin_dashboard():

        if "user_id" not in session:
            return redirect(url_for("login"))

        if session["role"] != "admin":
            return "Access Denied"

        total_users = User.query.filter_by(role="user").count()
        total_staff = User.query.filter_by(role="staff").count()
        total_treks = Trek.query.count()
        total_bookings = Booking.query.count()

        return render_template(
            "admin/dashboard.html",
            total_users=total_users,
            total_staff=total_staff,
            total_treks=total_treks,
            total_bookings=total_bookings
        )


    # ----------------------------
    # Staff Dashboard
    # ----------------------------
    @app.route("/staff/dashboard")
    def staff_dashboard():

        if "user_id" not in session:
            return redirect(url_for("login"))

        if session["role"] != "staff":
            return "Access Denied"

        return render_template("staff/dashboard.html")


    # ----------------------------
    # User Dashboard
    # ----------------------------
    @app.route("/user/dashboard")
    def user_dashboard():

        if "user_id" not in session:
            return redirect(url_for("login"))

        if session["role"] != "user":
            return "Access Denied"

        return render_template("user/dashboard.html")