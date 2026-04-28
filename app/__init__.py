"""
Flask Application Factory.
Smart Utility Expense Prediction System.
"""
import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URI",
        f"sqlite:///{Path(__file__).parent.parent / 'instance' / 'utility.db'}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.bills import bills_bp
    from .routes.predict import predict_bp
    from .routes.budget import budget_bp
    from .routes.payments import payments_bp
    from .routes.admin import admin_bp
    from .routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(bills_bp, url_prefix="/bills")
    app.register_blueprint(predict_bp, url_prefix="/predict")
    app.register_blueprint(budget_bp, url_prefix="/budget")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    with app.app_context():
        db.create_all()

    return app
