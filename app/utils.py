import json
from pathlib import Path

from app import db
from app.models import Card, UserCard
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
            continue

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


def add_user_cards(user_id: int, cards: list[tuple[str, int]]):
    """
    Add cards to a user.

    Args:
        user_id: id of user
        cards: list of (card_name, quantity) tuples
    """
    card_names = [name for name, _ in cards]
    db_cards = (db.session.query(Card).filter(Card.name.in_(card_names)).all())
    card_map = {card.name: card for card in db_cards}

    for card_name, quantity in cards:
        card = card_map.get(card_name)
        if not card:
            raise ValueError(f"Card '{card_name}' does not exist")

        for _ in range(quantity):
            user_card = UserCard(
                user_id=user_id,
                card_id=card.id,
                uses_remaining=card.uses
            )
            db.session.add(user_card)
