import click
from flask import Flask, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_login import LoginManager
from werkzeug.exceptions import RequestEntityTooLarge

db = SQLAlchemy()
migrate = Migrate()
login_manager=LoginManager()
login_manager.login_view='main.login'
login_manager.login_message="Please log in to access this page."
login_manager.login_message_category="warning"


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import models

    from app.routes import bp
    from app.inventory import bp as inventory_bp
    from app.trading import bp as trading_bp
    from app.shop import bp as shop_bp
    from app.profile import bp as profile_bp
    app.register_blueprint(bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(profile_bp)
    register_cli(app)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        flash("Profile photo is too large. Maximum size is 1MB.", "danger")
        return redirect(request.referrer or url_for("main.index"))

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return db.session.get(User, int(user_id))

from app.utils import seed_cards, give_all_cards


def register_cli(app):
    @app.cli.command("seed-cards")
    def seed_cards_command():
        """Seed the database with cards from JSON."""
        seed_cards()
        click.echo("Cards seeded!")

    @app.cli.command("give-all-cards")
    @click.argument("user_id", type=int)
    @click.option("--quantity", default=20, type=int)
    def give_all_cards_command(user_id, quantity):
        """Give a user copies of every card."""
        give_all_cards(user_id, quantity)
        db.session.commit()
        print(f"Gave user {user_id} {quantity} copies of every card.")
