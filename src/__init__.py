import logging
import os
from logging.handlers import RotatingFileHandler

import dotenv
from flask import Flask

from .api.auth_routes import auth_bp
from .api.data_routes import data_bp
from .api.insecure_routes import insecure_bp
from .config import Config
from .db import db, db_create_default_user


def create_app():
    app = Flask(__name__)
    dotenv.load_dotenv()
    app.config.from_object(Config)

    db.init_app(app)

    if not os.path.exists('logs'):
        os.mkdir('logs')

    fh = RotatingFileHandler('logs/app.log', maxBytes=10240)
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    fh.setLevel(logging.INFO)
    app.logger.addHandler(fh)

    app.logger.setLevel(logging.INFO)
    app.logger.info('App starting')

    app.register_blueprint(auth_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(insecure_bp)

    with app.app_context():
        db.create_all()
        db_create_default_user()

    return app
