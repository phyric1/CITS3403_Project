import json
from flask_login import current_user
from pathlib import Path
from sqlalchemy.orm import joinedload

from app import db
from app.models import Card, UserCard, Deck, DeckCard
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
        user_id (int): id of user
        cards: list of (card_name, quantity) tuples
    """
    card_names = [name for name, _ in cards]
    db_cards = (db.session.query(Card).filter(Card.name.in_(card_names)).all())
    card_map = {card.name: card for card in db_cards}

    for card_name, quantity in cards:
        card = card_map.get(card_name)
        if not card:
            raise ValueError(f"Card '{card_name}' does not exist")
        if card.type == CardType.debuff:
            raise ValueError("Cannot add debuff cards to user")

        for _ in range(quantity):
            user_card = UserCard(
                user_id=user_id,
                card_id=card.id,
                uses_remaining=card.uses
            )
            db.session.add(user_card)


def give_all_cards(user_id: int, quantity: int = 20):
    """
    Give a user `quantity` copies of every card.

    Args:
        user_id (int): id of user
        quantity (int): number of user_cards that is added for each card
    """
    cards = [
        (card.name, quantity)
        for card in Card.query.filter(Card.type!=CardType.debuff).all()
    ]
    add_user_cards(user_id, cards)


def get_current_user_id() -> tuple[int | None, tuple | None]:
    """
    Retrieve the ID of the currently authenticated user from the session.

    Returns:
        tuple:
            - int | None: The user's ID if authenticated, otherwise None.
            - tuple | None: An error response in the form (dict, status_code)
              if the user is not authenticated, otherwise None.

    """
    user_id = current_user.id
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
    deck = (Deck.query
            .options(joinedload(Deck.deck_cards).joinedload(DeckCard.user_card).joinedload(UserCard.card))
            .filter_by(user_id=user_id)
            .first())
    if not deck:
        return None, ({"error": "Deck not found"}, 404)
    return deck, None

def get_deck_cards(user_id: int):
    """
    Retrieves all cards in a deck
    """
    deck_query = (
        db.session.query(UserCard)
        .join(DeckCard, DeckCard.user_card_id == UserCard.id)
        .join(Deck, Deck.id == DeckCard.deck_id)
        .options(joinedload(UserCard.card))
        .filter(Deck.user_id == user_id, UserCard.user_id == user_id)
    )
    cards = deck_query.all()
    return cards

def compute_game_score(game):
    """
    Calclate and return game score of game object
    """
    return (
        (1 if game.isWin else 0) * 500 +
        (game.gameOverStats["goldCollected"] * 2) +
        (game.gameOverStats["enemiesDefeated"] * 25) +
        game.gameOverStats["turnsPlayed"] +
        (50 if game.isWin else 0)
    )
