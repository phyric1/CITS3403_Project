import json
from pathlib import Path

from app import db
from app.models import Card
from app.enums import CardRarity, CardType


def seed_cards():
    """Seed the database with cards from JSON."""
    path = Path(__file__).parent / "data" / "cards.json"

    with open(path) as f:
        data = json.load(f)

    for item in data:
        existing = Card.query.filter_by(name=item["name"]).first()
        if existing:
            existing.effect = item["effect"]
            existing.rarity = CardRarity(item["rarity"])
            existing.type = CardType(item["type"])
            existing.uses = item["uses"]
            existing.max_in_deck = item["max_in_deck"]

        card = Card(
            name=item["name"],
            effect=item["effect"],
            rarity=CardRarity(item["rarity"]),
            type=CardType(item["type"]),
            uses=item["uses"],
            max_in_deck=item["max_in_deck"]
        )

        db.session.add(card)
    db.session.commit()
