from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.model import User
from app import sessionLocal
auth_bp = Blueprint('register', __name__)
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from app.routes.create_admin import create_admin
    create_admin()
    if request.method == "POST":
        db = sessionLocal()
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.query(User).filter_by(username=username).first()
        db.close()

        if user and user.check_password(password):
            session.permanent = True  # ✅ Keeps session alive longer
            session['user'] = username
            session['is_admin'] = user.is_admin

            if user.is_admin:
                flash("Welcome Admin", 'info')
                return redirect(url_for('admin.admin_dashboard'))

            flash("Login Successful", 'success')
            return redirect(url_for("auth_google.authorize"))  # ✅ Redirect to Google Fit OAuth
        else:
            flash("Invalid username or password", 'danger')

    return render_template("login.html")
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = sessionLocal()
        form = request.form

        # Check if user or email exists
        if db.query(User).filter_by(username=form["username"]).first():
            flash("Username already exists.", "danger")
            db.close()
            return render_template("register.html")

        if db.query(User).filter_by(email=form["email"]).first():
            flash("Email already exists.", "danger")
            db.close()
            return render_template("register.html")

        # Create new user
        new_user = User(
            username=form["username"],
            hash_password=form["password"],
            name=form["name"],
            email=form["email"],
            age=int(form["age"]),
            gender=form["gender"],
            weight=float(form["weight"]),
            height=float(form["height"]),
            blood_group=form["blood_group"],
            contact=form["contact"]
        )
        new_user.set_password(form['password'])

        db.add(new_user)
        db.commit()
        db.close()

        flash("Registration successful!", "success")
        return redirect(url_for("register.login"))

    return render_template("register.html")
@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out", "info")
    return redirect(url_for("home.home"))  # Adjust route if needed
