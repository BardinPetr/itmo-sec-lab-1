import os
from datetime import datetime, timezone
from functools import wraps

import jwt
from flask import current_app as app, request, jsonify

from .db import User


def generate_jwt_token(user_id, username):
    now = datetime.now(timezone.utc)
    payload = {
        'iss': 'app',
        'sub': str(user_id),
        'username': username,
        'iat': now,
        'exp': now + app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'jti': os.urandom(16).hex()
    }
    return jwt.encode(payload,
                      app.config['JWT_SECRET_KEY'],
                      algorithm=app.config['JWT_ALGORITHM'])


def decode_jwt_token(token):
    try:
        return jwt.decode(token,
                          app.config['JWT_SECRET_KEY'],
                          algorithms=[app.config['JWT_ALGORITHM']])
    except jwt.ExpiredSignatureError:
        app.logger.warning(f"Auth failed: Token has expired: {token}")
    except jwt.InvalidTokenError as e:
        app.logger.warning(f"Auth failed: Token invalid: {token}: {e}")
    return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        token = request.args.get("token", token)

        if not token:
            app.logger.warning("Access denied: Missing auth token.")
            return jsonify({"msg": "Token is missing!"}), 401

        try:
            data = decode_jwt_token(token)
            if not data:
                return jsonify({"msg": "Token is invalid or expired!"}), 401

            usr = User.query.get(int(data['sub']))
            if not usr:
                app.logger.warning(f"Access denied: User with ID {data['sub']} not found for token.")
                return jsonify({"msg": "User not found!"}), 401
            request.current_user = usr

        except Exception as e:
            app.logger.error(f"Error during token verification: {e}")
            return jsonify({"msg": "Token is invalid!"}), 401

        return f(*args, **kwargs)

    return decorated


def require_roles(roles):
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if not (usr := request.current_user):
                app.logger.critical("Error: current_user not found after token_required decorator.")
                return jsonify({"msg": "Authentication error"}), 500

            if usr.role not in roles:
                app.logger.warning(
                    f"Access denied: User {usr.username} (role: {usr.role}) does not have required roles: {roles}")
                return jsonify({"msg": "Insufficient permissions"}), 403
            return f(*args, **kwargs)

        return decorated_function

    return decorator
