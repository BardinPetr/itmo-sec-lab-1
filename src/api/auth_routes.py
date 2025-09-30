from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import db, User
from ..security import generate_jwt_token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username, password = data.get('username'), data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        app.logger.warning(f"Register: Username '{username}' already exists.")
        return jsonify({"msg": "Already exists"}), 409

    password_hash = generate_password_hash(password, method='scrypt')
    new_user = User(username=username, password_hash=password_hash, role='USER')

    try:
        db.session.add(new_user)
        db.session.commit()
        app.logger.info(f"Register: User '{username}' registered successfully.")
        return jsonify({"msg": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Auth error: Error during user registration for '{username}': {e}")
        return jsonify({"msg": "Error registering user", "details": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username, password = data.get('username'), data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        app.logger.warning(f"Auth failed: Invalid credentials for user '{username}'.")
        return jsonify({"msg": "Invalid credentials"}), 401

    token = generate_jwt_token(user.id, user.username)
    app.logger.info(f"Auth success: User '{username}' logged in successfully.")
    return jsonify({"access_token": token}), 200
