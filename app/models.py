from sqlalchemy import event
# Use the built-in hash function in Flask to protect passwords
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.enums import TradeStatus, CardRarity, CardType

MAX_DECK_SIZE = 40


class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),index=True,unique=True,nullable=False)
    email=db.Column(db.String(128),index=True,unique=True,nullable=False)
    password_hash=db.Column(db.String(256),nullable=False)
    gold=db.Column(db.Integer,default=20,nullable=False)
    easy_tokens=db.Column(db.Integer,default=0)
    medium_tokens=db.Column(db.Integer,default=0)
    hard_tokens=db.Column(db.Integer,default=0)

    cards = db.relationship('UserCard', back_populates='user', cascade='all, delete-orphan')
    decks = db.relationship('Deck', back_populates='user', cascade='all, delete-orphan')
    sender_trades = db.relationship('Trade', foreign_keys='Trade.sender_id', back_populates='sender')
    receiver_trades = db.relationship('Trade', foreign_keys='Trade.receiver_id', back_populates='receiver')

    #Store the encrypted hash password
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    #Check if the password is correct or not
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f"<User {self.username}>"


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), index=True, unique=True, nullable=False)
    effect = db.Column(db.Text, nullable=False)
    rarity = db.Column(db.Enum(CardRarity, validate_strings=True, native_enum=False), nullable=False)
    type = db.Column(db.Enum(CardType, validate_strings=True, native_enum=False), nullable=False)
    duration = db.Column(db.Integer)
    uses = db.Column(db.Integer, nullable=False) # -1 for infinite uses
    max_in_deck = db.Column(db.Integer, nullable=False, default=1)

    __table_args__ = (
        db.CheckConstraint('max_in_deck >= -1', name='check_max_in_deck_positive'),
        db.CheckConstraint('uses >= -1', name='check_uses_positive'),
    )

    def __repr__(self):
        return f"<Card {self.name}>"


class UserCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False, index=True)
    uses_remaining = db.Column(db.Integer, nullable=False) # -1 for infinite uses
    tradable = db.Column(db.Boolean, nullable=False, default=False)
    protected = db.Column(db.Boolean, nullable=False, default=False)
    locked = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', back_populates='cards')
    card = db.relationship('Card')

    __table_args__ = (
        db.CheckConstraint('uses_remaining >= -1', name='check_uses_remaining_valid'),
    )

    def __repr__(self):
        return f"<UserCard user={self.user_id} card={self.card_id}>"


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    user = db.relationship('User', back_populates='decks')
    deck_cards = db.relationship('DeckCard', back_populates='deck', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Deck {self.name} (user={self.user_id})>"


class DeckCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False, index=True)
    user_card_id = db.Column(db.Integer, db.ForeignKey('user_card.id'), nullable=False)

    deck = db.relationship('Deck', back_populates='deck_cards')
    user_card = db.relationship('UserCard') # Cards specified in deck are abstract, and should be resolved to UserCards on game initialisation

    __table_args__ = (
        db.UniqueConstraint('deck_id', 'user_card_id', name='unique_card_per_deck'),
    )

    def __repr__(self):
        return f"<DeckCard deck={self.deck_id} card={self.user_card_id}>"


class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.Enum(TradeStatus, validate_strings=True, native_enum=False), default=TradeStatus.pending, nullable=False)
    creation_date = db.Column(db.DateTime, default=db.func.now(), nullable=False,)

    trade_cards = db.relationship('TradeCard', back_populates='trade', cascade='all, delete-orphan')
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sender_trades')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='receiver_trades')


class TradeCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'), nullable=False)
    user_card_id = db.Column(db.Integer, db.ForeignKey('user_card.id', ondelete='CASCADE'), nullable=False)

    user_card = db.relationship('UserCard', lazy='joined')
    trade = db.relationship('Trade', back_populates='trade_cards')

    __table_args__ = (
        db.UniqueConstraint('trade_id', 'user_card_id', name='unique_trade_card'),
    )


@event.listens_for(User, "after_insert")
def create_deck(mapper, connection, target):
    connection.execute(Deck.__table__.insert().values(user_id=target.id, name=f"{target.username}'s Deck"))

class DailyShopCard(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    card_id=db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False, index=True)
    date=db.Column(db.String(10), nullable=False)  # Format: YYYY-MM-DD
    user=db.relationship('User')
    card=db.relationship('Card')
    __table_args__ = (
        db.UniqueConstraint('user_id', 'card_id', 'date', name='unique_daily_shop_card'),
    )
