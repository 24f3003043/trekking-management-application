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

    # =========================================================================
    # ADMIN ROUTES
    # =========================================================================

    # Manage Users (Trekkers)
    @app.route("/admin/users")
    def admin_users():
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        q = request.args.get("q", "")
        if q:
            users = User.query.filter(
                User.role == "user",
                (User.name.like(f"%{q}%") | User.email.like(f"%{q}%") | User.phone.like(f"%{q}%"))
            ).all()
        else:
            users = User.query.filter_by(role="user").all()
        return render_template("admin/users.html", users=users, q=q)

    # Manage Staff
    @app.route("/admin/staff")
    def admin_staff():
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        q = request.args.get("q", "")
        if q:
            staff = User.query.filter(
                User.role == "staff",
                (User.name.like(f"%{q}%") | User.email.like(f"%{q}%") | User.phone.like(f"%{q}%"))
            ).all()
        else:
            staff = User.query.filter_by(role="staff").all()
        return render_template("admin/staff.html", staff=staff, q=q)

    # Approve Staff
    @app.route("/admin/staff/approve/<int:staff_id>")
    def admin_staff_approve(staff_id):
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        staff_member = User.query.get_or_404(staff_id)
        if staff_member.role == "staff":
            staff_member.approved = True
            db.session.commit()
        return redirect(url_for("admin_staff"))

    # Toggle Blacklist for User / Staff
    @app.route("/admin/user/toggle_blacklist/<int:user_id>")
    def admin_user_toggle_blacklist(user_id):
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        user = User.query.get_or_404(user_id)
        user.blacklisted = not user.blacklisted
        db.session.commit()
        from_page = request.args.get("from", "users")
        if from_page == "staff":
            return redirect(url_for("admin_staff"))
        return redirect(url_for("admin_users"))

    # Delete User / Staff
    @app.route("/admin/user/delete/<int:user_id>", methods=["POST"])
    def admin_user_delete(user_id):
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        user = User.query.get_or_404(user_id)
        if user.role == "staff":
            for trek in user.managed_treks:
                trek.staff_id = None
        elif user.role == "user":
            for booking in user.bookings:
                db.session.delete(booking)
        db.session.delete(user)
        db.session.commit()
        from_page = request.args.get("from", "users")
        if from_page == "staff":
            return redirect(url_for("admin_staff"))
        return redirect(url_for("admin_users"))

    # View Treks (Admin)
    @app.route("/admin/treks")
    def admin_treks():
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        q = request.args.get("q", "")
        if q:
            treks = Trek.query.filter(Trek.name.like(f"%{q}%") | Trek.location.like(f"%{q}%")).all()
        else:
            treks = Trek.query.all()
        return render_template("admin/treks.html", treks=treks, q=q)

    # Add Trek
    @app.route("/admin/treks/add", methods=["GET", "POST"])
    def admin_add_trek():
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        if request.method == "POST":
            name = request.form["name"]
            location = request.form["location"]
            difficulty = request.form["difficulty"]
            duration = int(request.form["duration"])
            available_slots = int(request.form["available_slots"])
            status = request.form["status"]
            description = request.form.get("description", "")
            
            start_date_str = request.form.get("start_date")
            end_date_str = request.form.get("end_date")
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
            
            staff_id = request.form.get("staff_id")
            staff_id = int(staff_id) if staff_id else None

            trek = Trek(
                name=name,
                location=location,
                difficulty=difficulty,
                duration=duration,
                available_slots=available_slots,
                status=status,
                description=description,
                start_date=start_date,
                end_date=end_date,
                staff_id=staff_id
            )
            db.session.add(trek)
            db.session.commit()
            return redirect(url_for("admin_treks"))

        staff = User.query.filter_by(role="staff", approved=True).all()
        return render_template("admin/add_trek.html", staff=staff)

    # Edit Trek
    @app.route("/admin/treks/edit/<int:trek_id>", methods=["GET", "POST"])
    def admin_edit_trek(trek_id):
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        trek = Trek.query.get_or_404(trek_id)
        if request.method == "POST":
            trek.name = request.form["name"]
            trek.location = request.form["location"]
            trek.difficulty = request.form["difficulty"]
            trek.duration = int(request.form["duration"])
            trek.available_slots = int(request.form["available_slots"])
            trek.status = request.form["status"]
            trek.description = request.form.get("description", "")
            
            start_date_str = request.form.get("start_date")
            end_date_str = request.form.get("end_date")
            trek.start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
            trek.end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
            
            staff_id = request.form.get("staff_id")
            trek.staff_id = int(staff_id) if staff_id else None

            db.session.commit()
            return redirect(url_for("admin_treks"))

        staff = User.query.filter_by(role="staff", approved=True).all()
        return render_template("admin/edit_trek.html", trek=trek, staff=staff)

    # Delete Trek
    @app.route("/admin/treks/delete/<int:trek_id>", methods=["POST"])
    def admin_delete_trek(trek_id):
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        trek = Trek.query.get_or_404(trek_id)
        for booking in trek.bookings:
            db.session.delete(booking)
        db.session.delete(trek)
        db.session.commit()
        return redirect(url_for("admin_treks"))

    # View All Bookings (Admin)
    @app.route("/admin/bookings")
    def admin_bookings():
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
        return render_template("admin/bookings.html", bookings=bookings)

    # Cancel Booking (Admin/User fallback)
    @app.route("/admin/booking/cancel/<int:booking_id>", methods=["POST"])
    def admin_cancel_booking(booking_id):
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        booking = Booking.query.get_or_404(booking_id)
        if booking.status == "Booked":
            booking.status = "Cancelled"
            booking.trek.available_slots += 1
            db.session.commit()
        return redirect(url_for("admin_bookings"))

    # Trek History & Status Tracking Page (Admin)
    @app.route("/admin/trek-history")
    def admin_trek_history():
        if "user_id" not in session or session["role"] != "admin":
            return "Access Denied"
        treks = Trek.query.order_by(Trek.start_date.desc()).all()
        return render_template("admin/trek_history.html", treks=treks)

    # =========================================================================
    # STAFF ROUTES
    # =========================================================================

    # Staff Profile
    @app.route("/staff/profile", methods=["GET", "POST"])
    def staff_profile():
        if "user_id" not in session or session["role"] != "staff":
            return "Access Denied"
        user = User.query.get_or_404(session["user_id"])
        msg = None
        if request.method == "POST":
            user.name = request.form["name"]
            user.phone = request.form.get("phone", "")
            user.experience_years = int(request.form["experience_years"] or 0)
            user.skills = request.form.get("skills", "")
            user.bio = request.form.get("bio", "")
            
            new_password = request.form.get("password")
            if new_password:
                user.password = generate_password_hash(new_password)
                
            db.session.commit()
            msg = "Profile updated successfully!"
        return render_template("staff/profile.html", user=user, msg=msg)

    # Assigned Treks
    @app.route("/staff/treks")
    def staff_treks():
        if "user_id" not in session or session["role"] != "staff":
            return "Access Denied"
        treks = Trek.query.filter_by(staff_id=session["user_id"]).all()
        return render_template("staff/treks.html", treks=treks)

    # Manage Assigned Trek
    @app.route("/staff/treks/<int:trek_id>", methods=["GET", "POST"])
    def staff_manage_trek(trek_id):
        if "user_id" not in session or session["role"] != "staff":
            return "Access Denied"
        trek = Trek.query.get_or_404(trek_id)
        if trek.staff_id != session["user_id"]:
            return "Access Denied"
            
        msg = None
        if request.method == "POST":
            trek.available_slots = int(request.form["available_slots"])
            trek.status = request.form["status"]
            db.session.commit()
            msg = "Trek status and slots updated successfully!"
            
        bookings = Booking.query.filter_by(trek_id=trek.id).order_by(Booking.booking_date.desc()).all()
        return render_template("staff/manage_trek.html", trek=trek, bookings=bookings, msg=msg)

    # Cancel Participant Booking (Staff)
    @app.route("/staff/treks/<int:trek_id>/participants/<int:booking_id>/cancel", methods=["POST"])
    def staff_cancel_participant(trek_id, booking_id):
        if "user_id" not in session or session["role"] != "staff":
            return "Access Denied"
        trek = Trek.query.get_or_404(trek_id)
        if trek.staff_id != session["user_id"]:
            return "Access Denied"
        booking = Booking.query.get_or_404(booking_id)
        if booking.trek_id != trek.id:
            return "Invalid Booking for this Trek"
            
        if booking.status == "Booked":
            booking.status = "Cancelled"
            trek.available_slots += 1
            db.session.commit()
            
        return redirect(url_for("staff_manage_trek", trek_id=trek.id))

    # =========================================================================
    # USER ROUTES
    # =========================================================================

    # Browse and Search Treks
    @app.route("/user/treks")
    def user_treks():
        if "user_id" not in session or session["role"] != "user":
            return "Access Denied"
            
        location = request.args.get("location", "")
        difficulty = request.args.get("difficulty", "")
        
        query = Trek.query.filter_by(status="Open")
        if location:
            query = query.filter(Trek.location.like(f"%{location}%"))
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
            
        treks = query.all()
        
        # Find already booked trek IDs to disable button
        bookings = Booking.query.filter_by(user_id=session["user_id"], status="Booked").all()
        booked_trek_ids = {b.trek_id for b in bookings}
        
        return render_template("user/treks.html", treks=treks, location=location, difficulty=difficulty, booked_trek_ids=booked_trek_ids)

    # Book a Trek
    @app.route("/user/book/<int:trek_id>", methods=["POST"])
    def user_book_trek(trek_id):
        if "user_id" not in session or session["role"] != "user":
            return "Access Denied"
            
        trek = Trek.query.get_or_404(trek_id)
        
        # Validations
        if trek.status != "Open":
            return "Booking failed: This trek is not open."
            
        if trek.available_slots <= 0:
            return "Booking failed: No slots available."
            
        existing_booking = Booking.query.filter_by(user_id=session["user_id"], trek_id=trek.id, status="Booked").first()
        if existing_booking:
            return "Booking failed: You have already booked this trek."
            
        # Book the trek
        trek.available_slots -= 1
        booking = Booking(
            user_id=session["user_id"],
            trek_id=trek.id,
            status="Booked"
        )
        db.session.add(booking)
        db.session.commit()
        
        return redirect(url_for("user_bookings"))

    # View User Bookings and History
    @app.route("/user/bookings")
    def user_bookings():
        if "user_id" not in session or session["role"] != "user":
            return "Access Denied"
            
        bookings = Booking.query.filter_by(user_id=session["user_id"]).order_by(Booking.booking_date.desc()).all()
        return render_template("user/bookings.html", bookings=bookings)

    # Cancel Booking (User)
    @app.route("/user/booking/cancel/<int:booking_id>", methods=["POST"])
    def user_cancel_booking(booking_id):
        if "user_id" not in session or session["role"] != "user":
            return "Access Denied"
            
        booking = Booking.query.get_or_404(booking_id)
        if booking.user_id != session["user_id"]:
            return "Access Denied"
            
        if booking.status == "Booked":
            booking.status = "Cancelled"
            booking.trek.available_slots += 1
            db.session.commit()
            
        return redirect(url_for("user_bookings"))