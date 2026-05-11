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
    from app.shop import bp as shop_bp
    app.register_blueprint(bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(shop_bp)
    register_cli(app)

    return app


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
