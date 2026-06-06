from flask import (Blueprint, render_template, request, jsonify, redirect)
from werkzeug.security import (generate_password_hash, check_password_hash)
from flask_login import (login_user, logout_user, current_user, login_required)
from .models import (db, User)

auth = Blueprint("auth", __name__)

@auth.route("/login")
def login_page():
    #Login page render
    return render_template("login.html")

@auth.route("/register")
def register_page():
    #Register page render
    return render_template("register.html")

#Register API
@auth.route("/api/register", methods=["POST"])
def register():

    #Get JSON data from frontend
    data = request.get_json()

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    #Validate username
    if not username:
        return jsonify({
            "success": False,
            "message": "Username required"
        })

    #Validate email
    if not email:
        return jsonify({
            "success": False,
            "message": "Email required"
        })

    #Validate password length
    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be 6+ characters"
        })

    #Check if user already exists
    existing = User.query.filter_by(email=email).first()

    if existing:
        return jsonify({
            "success": False,
            "message": "Email already exists"
        })

    #Create new user
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True})

#Login API
@auth.route("/api/login", methods=["POST"])
def login():

    #Get login data
    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    #Find user
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        })

    #Check password
    if not check_password_hash(user.password_hash, password):
        return jsonify({
            "success": False,
            "message": "Incorrect password"
        })

    #Login user session
    login_user(user)

    return jsonify({"success": True})

#Getting the current user
@auth.route("/api/user")
def current_user_info():

    if current_user.is_authenticated:
        return jsonify({
            "logged_in": True,
            "username": current_user.username,
            "email": current_user.email
        })

    return jsonify({"logged_in": False})

#Logout API
@auth.route("/api/logout")
def api_logout():

    logout_user()

    return jsonify({"success": True})

#Logout Page
@auth.route("/logout")
@login_required
def logout_page():

    logout_user()
    return redirect("/")