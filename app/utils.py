import json
from flask import session
from pathlib import Path

from app import db
from app.models import Card, UserCard, Deck
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


def get_current_user_id() -> tuple[int | None, tuple | None]:
    """
    Retrieve the ID of the currently authenticated user from the session.

    Returns:
        tuple:
            - int | None: The user's ID if authenticated, otherwise None.
            - tuple | None: An error response in the form (dict, status_code)
              if the user is not authenticated, otherwise None.

    """
    user_id = session.get("user_id")
    if not user_id:
        return None, ({"error": "Unauthorized"}, 401)
    return user_id, None


def get_user_card(user_id: int, user_card_id: int) -> tuple[UserCard | None, tuple | None]:
    """
    Retrieve a UserCard belonging to a specific user.
    Args:
        user_id (int): ID of the user who should own the card.
        user_card_id (int): ID of the UserCard to retrieve.

    Returns:
        tuple:
            - UserCard | None: The matching UserCard if found and owned by the user.
            - tuple | None: An error response in the form (dict, status_code)
              if the card does not exist or is not owned by the user.
    """
    user_card = UserCard.query.filter_by(id=user_card_id, user_id=user_id).first()
    if not user_card:
        return None, ({"error": "Card not found"}, 404)
    return user_card, None


def get_user_deck(user_id: int) -> tuple[Deck | None, tuple | None]:
    """
    Retrieve the deck associated with a given user.

    Args:
        user_id (int): ID of the user whose deck should be retrieved.

    Returns:
        tuple:
            - Deck | None: The user's Deck if it exists.
            - tuple | None: An error response in the form (dict, status_code)
              if no deck is found for the user.
    """
    deck = Deck.query.filter_by(user_id=user_id).first()
    if not deck:
        return None, ({"error": "Deck not found"}, 404)
    return deck, None
