import html

from flask import Blueprint, request, jsonify, current_app

from ..db import db, Cat
from ..security import require_auth, require_roles

data_bp = Blueprint('data', __name__, url_prefix='/api')


@data_bp.route('/data', methods=['GET'])
@require_auth
def get_all_cats():
    cats = Cat.query.all()
    current_app.logger.info(f"Data access: User {request.current_user.username} accessed all cat data.")
    page = "\n".join(f"<li>{i.name}: {i.color}</li>" for i in cats)
    page = f"<ul>\n{page}\n</ul>"
    return page, 200


@data_bp.route('/add', methods=['POST'])
@require_roles(['ADMIN'])
def add_cat():
    data = request.get_json()
    name = data.get('name')
    color = data.get('color')
    if not name or not color:
        return jsonify({"msg": "Missing name or color"}), 400

    try:
        db.session.add(Cat(
            name=html.escape(name),
            color=html.escape(color)
        ))
        db.session.commit()
        current_app.logger.info(
            f"User {request.current_user.username} added cat: {name}/{color}.")
        return jsonify({"msg": "Cat added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Data add error by user {request.current_user.username}: {e}")
        return jsonify({"msg": "Error adding cat"}), 500
