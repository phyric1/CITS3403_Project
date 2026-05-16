import pytest
from app import create_app, db
from app.models import User, Card, UserCard, Trade, TradeCard
from app.enums import CardRarity, CardType


@pytest.fixture()
def app(tmp_path):
    test_db = tmp_path / "test.db"
    test_db_uri = "sqlite:///" + str(test_db).replace("\\", "/")
    flask_app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": test_db_uri,
        "SECRET_KEY": "test_secret_key"
    })
    database_uri = flask_app.config["SQLALCHEMY_DATABASE_URI"]
    assert "test.db" in database_uri
    assert "app.db" not in database_uri
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        seed_test_cards()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(app):
    with app.app_context():
        user=User(username="test",email="test@test.com")
        user.set_password("test1234")
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture()
def login(client):
    def do_login(username="test",password="test1234"):
        return client.post("/login",data={"username":username,"password":password}, follow_redirects=True)
    return do_login

def seed_test_cards():
    cards=[
         Card(
            name="Silence Falls",
            effect="Stealth +1",
            rarity=CardRarity.common,
            type=CardType.utility,
            uses=-1,
            max_in_deck=3
        ),
        Card(
            name="Tailwind",
            effect="Move 2 spaces without triggering enemy behavior",
            rarity=CardRarity.common,
            type=CardType.movement,
            uses=7,
            max_in_deck=3
        ),
        Card(
            name="Dagger",
            effect="Deal damage to an enemy",
            rarity=CardRarity.common,
            type=CardType.combat,
            uses=3,
            max_in_deck=3
        ),
        Card(
            name="Dexterity",
            effect="Improve movement ability",
            rarity=CardRarity.uncommon,
            type=CardType.utility,
            uses=3,
            max_in_deck=1
        ),
        Card(
            name="Rest",
            effect="Recover health",
            rarity=CardRarity.common,
            type=CardType.survival,
            uses=2,
            max_in_deck=2
        ),
        Card(
            name="Shop Test Card",
            effect="A test card for shop display",
            rarity=CardRarity.rare,
            type=CardType.utility,
            uses=3,
            max_in_deck=3
        ),
    ]
    for card in cards:
        existing_card = Card.query.filter_by(name=card.name).first()
        if existing_card is None:
            db.session.add(card)
    db.session.commit()




@pytest.fixture()
def second_user(app):
    with app.app_context():
        user = User(username="other", email="other@test.com")
        user.set_password("test1234")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture()
def login_as(client):
    def do_login(username, password="test1234"):
        return client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True
        )
    return do_login


@pytest.fixture()
def give_user_card(app):
    def do_give_user_card(user_id, card_name, tradable=True, locked=False, uses_remaining=3):
        card = Card.query.filter_by(name=card_name).first()
        user_card = UserCard(
            user_id=user_id,
            card_id=card.id,
            tradable=tradable,
            locked=locked,
            uses_remaining=uses_remaining
        )
        db.session.add(user_card)
        db.session.commit()
        return user_card.id
    return do_give_user_card

@pytest.fixture()
def create_test_trade(app, give_user_card):
    def do_create_test_trade(sender_id, receiver_id, receiver_viewed=False):
        with app.app_context():
            sender_card_id = give_user_card(sender_id, "Dagger", tradable=True, locked=True, uses_remaining=3)
            receiver_card_id = give_user_card(receiver_id, "Tailwind", tradable=True, locked=True, uses_remaining=7)

            trade = Trade(sender_id=sender_id, receiver_id=receiver_id, receiver_viewed=receiver_viewed)
            db.session.add(trade)
            db.session.flush()

            db.session.add(TradeCard(trade_id=trade.id, user_card_id=sender_card_id))
            db.session.add(TradeCard(trade_id=trade.id, user_card_id=receiver_card_id))
            db.session.commit()

            return trade.id, sender_card_id, receiver_card_id
    return do_create_test_trade


