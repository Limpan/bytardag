import logging

from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


__version__ = "0.1.0"

db = SQLAlchemy()


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    print(app.config["SQLALCHEMY_DATABASE_URI"])

    db.init_app(app)

    from bytardag.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        # Log to STDOUT
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)

    app.logger.info("Bytardag startup.")

    return app


from bytardag import models  # noqa: E402, F401, I100, I202