from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db,User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "user exists"}), 400

    hashed = generate_password_hash(password)
    user = User(username=username, password_hash=hashed)
    db.session.add(user)
    db.session.commit()

    return jsonify({"ok": True})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid creds"}), 401

    login_user(user)   # sets session cookie
    return jsonify({"ok": True, "user_id": user.id})

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"ok": True})

@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({"id": current_user.id, "username": current_user.username})
