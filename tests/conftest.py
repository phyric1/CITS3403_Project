import pytest
from app import create_app, db
from app.models import User,Card
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



