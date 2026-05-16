from app.models import Card


def test_market_requires_login(client):
    response = client.get("/market")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_market_page_loads(client, user, login):
    login()
    response = client.get("/market")
    assert response.status_code == 200
    assert b"Trade Market" in response.data


def test_market_shows_no_cards_when_no_tradable_copies(client, user, login):
    login()
    response = client.get("/market")
    assert response.status_code == 200
    assert b"No Cards" in response.data


def test_market_shows_view_cards_when_tradable_copy_exists(client, app, user, login, give_user_card):
    with app.app_context():
        give_user_card(user, "Dagger", tradable=True, locked=False, uses_remaining=3)

    login()
    response = client.get("/market")
    assert response.status_code == 200
    assert b"View Cards" in response.data
    assert b"Dagger" in response.data


def test_market_card_page_loads(client, app, user, login, give_user_card):
    with app.app_context():
        card = Card.query.filter_by(name="Dagger").first()
        card_id = card.id
        give_user_card(user, "Dagger", tradable=True, locked=False, uses_remaining=3)

    login()
    response = client.get(f"/market/{card_id}")
    assert response.status_code == 200
    assert b"Dagger" in response.data


def test_market_card_page_shows_owned_for_your_card(client, app, user, login, give_user_card):
    with app.app_context():
        card = Card.query.filter_by(name="Dagger").first()
        card_id = card.id
        give_user_card(user, "Dagger", tradable=True, locked=False, uses_remaining=3)

    login()
    response = client.get(f"/market/{card_id}")
    assert response.status_code == 200
    assert b"Owned" in response.data


def test_market_card_page_shows_trade_for_other_users_card(client, app, user, second_user, login, give_user_card):
    with app.app_context():
        card = Card.query.filter_by(name="Tailwind").first()
        card_id = card.id
        give_user_card(second_user, "Tailwind", tradable=True, locked=False, uses_remaining=7)

    login()
    response = client.get(f"/market/{card_id}")
    assert response.status_code == 200
    assert b"Trade" in response.data


def test_trade_from_market_prefills_new_trade(client, app, user, second_user, login, give_user_card):
    with app.app_context():
        other_card_id = give_user_card(second_user, "Tailwind", tradable=True, locked=False, uses_remaining=7)

    login()
    response = client.get(f"/trading/start/{other_card_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"New Trade" in response.data
    assert b"other" in response.data

    with client.session_transaction() as sess:
        assert sess["trade_target_username"] == "other"
        assert sess["requested_card_ids"] == [other_card_id]
        assert sess["offered_card_ids"] == []
