from app import db
from app.models import User, Card, UserCard, Trade, TradeCard


def test_trading_requires_login(client):
    response = client.get("/trading")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_trading_page_loads(client, user, login):
    login()
    response = client.get("/trading")
    assert response.status_code == 200
    assert b"Trading" in response.data
    assert b"Incoming Trades" in response.data
    assert b"Outgoing Trades" in response.data


def test_new_trade_page_loads(client, user, login):
    login()
    response = client.get("/trading/new")
    assert response.status_code == 200
    assert b"New Trade" in response.data
    assert b"Your Tradable Cards" in response.data


def test_new_trade_self_target_shows_error(client, user, login):
    login()
    response = client.get("/trading/new?target_username=test")
    assert response.status_code == 200
    assert b"You cannot trade with yourself." in response.data


def test_new_trade_invalid_target_shows_error(client, user, login):
    login()
    response = client.get("/trading/new?target_username=missing")
    assert response.status_code == 200
    assert b"User not found." in response.data


def test_submit_trade_creates_trade(client, app, user, second_user, login, give_user_card):
    with app.app_context():
        sender_card_id = give_user_card(user, "Dagger", tradable=True, locked=False, uses_remaining=3)
        receiver_card_id = give_user_card(second_user, "Tailwind", tradable=True, locked=False, uses_remaining=7)

    login()

    with client.session_transaction() as sess:
        sess["trade_target_username"] = "other"
        sess["requested_card_ids"] = [receiver_card_id]
        sess["offered_card_ids"] = [sender_card_id]

    response = client.post(
        "/trading/new/submit",
        data={"target_username": "other"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Trading" in response.data

    with app.app_context():
        trade = Trade.query.first()
        assert trade is not None
        assert trade.sender_id == user
        assert trade.receiver_id == second_user
        assert trade.receiver_viewed is False

        trade_cards = TradeCard.query.filter_by(trade_id=trade.id).all()
        assert len(trade_cards) == 2

        sender_card_db = db.session.get(UserCard, sender_card_id)
        receiver_card_db = db.session.get(UserCard, receiver_card_id)
        assert sender_card_db.locked is True
        assert receiver_card_db.locked is True



def test_view_trade_page_loads_for_sender(client, user, second_user, login, create_test_trade):
    trade_id, sender_card_id, receiver_card_id = create_test_trade(user, second_user)

    login()

    response = client.get(f"/trading/{trade_id}")
    assert response.status_code == 200
    assert b"Trade Details" in response.data
    assert b"Dagger" in response.data
    assert b"Tailwind" in response.data


def test_viewing_trade_as_receiver_sets_viewed_true(client, app, user, second_user, login_as, create_test_trade):
    trade_id, sender_card_id, receiver_card_id = create_test_trade(user, second_user, receiver_viewed=False)

    login_as("other")

    response = client.get(f"/trading/{trade_id}")
    assert response.status_code == 200

    with app.app_context():
        trade = db.session.get(Trade, trade_id)
        assert trade.receiver_viewed is True


def test_receiver_can_accept_trade(client, app, user, second_user, login_as, create_test_trade):
    trade_id, sender_card_id, receiver_card_id = create_test_trade(user, second_user)

    login_as("other")

    response = client.post(
        f"/trading/{trade_id}/action",
        data={"action": "accept"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Trading" in response.data

    with app.app_context():
        trade = db.session.get(Trade, trade_id)
        assert trade is None

        sender_card_db = db.session.get(UserCard, sender_card_id)
        receiver_card_db = db.session.get(UserCard, receiver_card_id)

        assert sender_card_db.user_id == second_user
        assert receiver_card_db.user_id == user
        assert sender_card_db.locked is False
        assert receiver_card_db.locked is False


def test_receiver_can_reject_trade(client, app, user, second_user, login_as, create_test_trade):
    trade_id, sender_card_id, receiver_card_id = create_test_trade(user, second_user)

    login_as("other")

    response = client.post(
        f"/trading/{trade_id}/action",
        data={"action": "reject"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Trading" in response.data

    with app.app_context():
        trade = db.session.get(Trade, trade_id)
        assert trade is None

        sender_card_db = db.session.get(UserCard, sender_card_id)
        receiver_card_db = db.session.get(UserCard, receiver_card_id)

        assert sender_card_db.user_id == user
        assert receiver_card_db.user_id == second_user
        assert sender_card_db.locked is False
        assert receiver_card_db.locked is False


def test_sender_can_cancel_trade(client, app, user, second_user, login, create_test_trade):
    trade_id, sender_card_id, receiver_card_id = create_test_trade(user, second_user)

    login()

    response = client.post(
        f"/trading/{trade_id}/action",
        data={"action": "cancel"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Trading" in response.data

    with app.app_context():
        trade = db.session.get(Trade, trade_id)
        assert trade is None

        sender_card_db = db.session.get(UserCard, sender_card_id)
        receiver_card_db = db.session.get(UserCard, receiver_card_id)

        assert sender_card_db.user_id == user
        assert receiver_card_db.user_id == second_user
        assert sender_card_db.locked is False
        assert receiver_card_db.locked is False
