import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', os.urandom(24).hex())
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=60)
    JWT_ALGORITHM = 'HS256'
