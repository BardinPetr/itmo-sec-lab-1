from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='USER')

    def __repr__(self):
        return f'<User {self.username} role={self.role}>'


class Cat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    color = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Cat {self.name} clr={self.color}>'


def db_create_default_user():
    if User.query.filter_by(role='ADMIN').count() == 0:
        db.session.add(User(username="admin", password_hash=generate_password_hash("admin"), role='ADMIN'))
        db.session.commit()
