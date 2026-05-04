import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.routes import bp
    from app.inventory import bp as inventory_bp
    app.register_blueprint(bp)
    app.register_blueprint(inventory_bp)
    register_cli(app)

    return app


from app.utils import seed_cards


def register_cli(app):
    @app.cli.command("seed-cards")
    def seed_cards_command():
        """Seed the database with cards from JSON."""
        seed_cards()
        click.echo("Cards seeded!")
