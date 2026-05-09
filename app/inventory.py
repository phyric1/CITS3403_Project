from flask import Blueprint, render_template, request, session, jsonify
from app import db
from app.models import User, Card, UserCard, Deck, DeckCard, MAX_DECK_SIZE
from app.utils import get_current_user_id, get_user_card, get_user_deck
from sqlalchemy import case, func

bp = Blueprint("inventory", __name__)


@bp.route("/profile/<username>/inventory")
def inventory(username):
    user = User.query.filter_by(username=username).first_or_404()
    is_owner = (session.get('user_id')) == user.id

    mode = request.args.get("mode", "view")
    if not is_owner:
        mode = "view"

    # Card Queries
    cards_in_deck_query = (db.session.query(DeckCard.user_card_id)
        .join(Deck, Deck.id == DeckCard.deck_id).filter(Deck.user_id == user.id))

    conditions = [UserCard.user_id == user.id, ~UserCard.id.in_(cards_in_deck_query)]
    if not is_owner:
        conditions.append(UserCard.tradable)

    if mode in ["view", "deck"]:
        card_query = (
            db.session
            .query(func.group_concat(UserCard.id, ",").label("user_card_ids"), UserCard.card_id, UserCard.uses_remaining, func.count(UserCard.id).label("quantity"), Card)
            .join(Card).filter(*conditions)
            .group_by(UserCard.card_id, UserCard.uses_remaining, Card.id))
    else:
        card_query = (db.session.query(UserCard).join(Card)
        .filter(*conditions))

    deck_query = (
        db.session.query(UserCard).join(Card)
        .join(DeckCard, DeckCard.user_card_id == UserCard.id)
        .join(Deck, Deck.id == DeckCard.deck_id)
        .filter(Deck.user_id == user.id, UserCard.user_id == user.id))

    # Sorting
    sort = request.args.get("sort")

    if sort == "name":
        card_query = card_query.order_by(Card.name)
        deck_query = deck_query.order_by(Card.name)
    elif sort == "rarity":
        rarity_order = {"common": 0, "rare": 1, "epic": 2, "legendary": 3, "master": 4}
        card_query = card_query.order_by(case(rarity_order, value=Card.rarity))
        deck_query = deck_query.order_by(case(rarity_order, value=Card.rarity))
    elif sort == "type":
        card_query = card_query.order_by(Card.type)
        deck_query = deck_query.order_by(Card.type)
    elif sort == "max":
        deck_query = deck_query.order_by(Card.max_in_deck.desc())
    elif sort == "uses":
        card_query = card_query.order_by(
            case((UserCard.uses_remaining == -1, 1), else_=0),
            UserCard.uses_remaining.desc())

    # Pagination
    page = request.args.get("page", 1, type=int)
    pagination = card_query.paginate(page=page, per_page=99, error_out=False)

    user_cards = pagination.items
    deck_cards = deck_query.all()

    return render_template("inventory.html",
        cards=user_cards,
        deck_cards=deck_cards,
        username=username,
        is_owner=is_owner,
        mode=mode,
        pagination=pagination,
        deck_size=len(deck_cards),
        max_deck_size=MAX_DECK_SIZE)


@bp.route("/api/deck/add", methods=["POST"]) # Potentially refactor to avoid repetition with remove route
def add_to_deck():
    user_id, err = get_current_user_id()
    if err:
        return err

    data = request.get_json()

    try:
        user_card_id = int(data.get("user_card_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user_card_id"}), 400
    if not user_card_id:
        return jsonify({"error": "Missing user_card_id"}), 400

    user_card, err = get_user_card(user_id, user_card_id)
    if err:
        return err

    deck, err = get_user_deck(user_id)
    if err:
        return err

    if DeckCard.query.filter_by(deck_id=deck.id).count() >= MAX_DECK_SIZE:
        return jsonify({"error": "Deck is full"}), 400

    if DeckCard.query.filter_by(deck_id=deck.id, user_card_id=user_card.id).first():
        return jsonify({"error": "Card already in users deck"}), 400

    count_same_card = (db.session.query(DeckCard).join(UserCard)
        .filter(DeckCard.deck_id == deck.id, UserCard.card_id == user_card.card_id).count())
    max_copies = user_card.card.max_in_deck
    if max_copies and max_copies <= count_same_card:
        return jsonify({"error": "Max copies of card in deck reached"}), 400

    db.session.add(DeckCard(deck_id=deck.id, user_card_id=user_card.id))
    user_card.tradable = False
    db.session.commit()
    return {"success": True}


@bp.route("/api/deck/remove", methods=["POST"])
def remove_from_deck():
    user_id, err = get_current_user_id()
    if err:
        return err

    data = request.get_json()

    try:
        user_card_id = int(data.get("user_card_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user_card_id"}), 400
    if not user_card_id:
        return jsonify({"error": "Missing user_card_id"}), 400

    deck, err = get_user_deck(user_id)
    if err:
        return err

    deck_card = DeckCard.query.join(UserCard).filter(DeckCard.deck_id == deck.id, UserCard.id == user_card_id, UserCard.user_id == user_id).first()

    if not deck_card:
        return jsonify({"error": "Card not in deck"}), 404

    db.session.delete(deck_card)
    db.session.commit()

    return {"success": True}


@bp.route("/api/user_card/tradable", methods=["POST"])
def tradable():
    user_id, err = get_current_user_id()
    if err:
        return err

    data = request.get_json()

    value = data.get("value")
    if not isinstance(value, bool):
        return jsonify({"error": "Invalid tradable value"}), 400

    try:
        user_card_id = int(data.get("user_card_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user_card_id"}), 400
    if not user_card_id:
        return jsonify({"error": "Missing user_card_id"}), 400

    user_card, err = get_user_card(user_id, user_card_id)
    if err:
        return err

    deck_entry = DeckCard.query.filter_by(user_card_id=user_card.id).first()
    if deck_entry:
        return jsonify({"error": "Card is in a deck and cannot have its tradability adjusted"}), 400

    user_card.tradable = value
    db.session.commit()

    return {"success": True}
