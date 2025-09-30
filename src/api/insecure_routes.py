from flask import Blueprint, request, jsonify

from ..db import db, Cat
from ..security import require_roles, generate_jwt_token

insecure_bp = Blueprint('insecure', __name__, url_prefix='/insecure')


@insecure_bp.route('/login', methods=['POST'])
def insecure_sqli():
    """
    Intentionally vulnerable for SQLi
    Example:
        POST http://localhost:5000/insecure/login
        Body:
        {
            "username": "admin' or 'a'='a",
            "password": "invalid_password_haha_sqli"
        }
    """
    username = request.get_json().get('username')

    phash = 'only_sql_i_can_pass--this_is_stub_for_password_has'
    query = f"SELECT id, username, password_hash FROM user WHERE password_hash = '{phash}' AND username = '{username}'"
    result = db.engine.connect().execute(db.text(query))
    result = result.fetchone()
    if result is not None:
        token = generate_jwt_token(result[0], result[1])
        return jsonify({"access_token": token}), 200
    return jsonify({"error": "err"}), 401


@insecure_bp.route('/add', methods=['POST'])
@require_roles(['ADMIN'])
def insecure_xss():
    """
    Intentionally vulnerable for XSS
    Example:
        POST http://localhost:5000/insecure/add
        Body:
        {
            "name": "<script>alert('XSS');</script>",
            "color": "Black"
        }
    """
    data = request.get_json()
    db.session.add(Cat(name=data.get('name'), color=data.get('color')))
    db.session.commit()
    return jsonify({"msg": "Cat added successfully"}), 201
