import pytest
from app import create_app,db
from app.models import User,UserCard,Deck,DeckCard,Trade,TradeCard,DailyShopCard,Game,GameStats,LifeTimeStats

def cleanup_test_users():
    flask_app = create_app()
    with flask_app.app_context():
        test_users=User.query.filter(User.username.like("selenium%")).all()
        user_ids=[user.id for user in test_users]
        if not user_ids:
            return
        trades=Trade.query.filter((Trade.sender_id.in_(user_ids)) | (Trade.receiver_id.in_(user_ids))).all()
        trade_ids=[trade.id for trade in trades]
        if trade_ids:
            TradeCard.query.filter(TradeCard.trade_id.in_(trade_ids)).delete(synchronize_session=False)
            Trade.query.filter(Trade.id.in_(trade_ids)).delete(synchronize_session=False)
        DailyShopCard.query.filter(DailyShopCard.user_id.in_(user_ids)).delete(synchronize_session=False)
        Game.query.filter(Game.user_id.in_(user_ids)).delete(synchronize_session=False)
        GameStats.query.filter(GameStats.user_id.in_(user_ids)).delete(synchronize_session=False)
        LifeTimeStats.query.filter(LifeTimeStats.user_id.in_(user_ids)).delete(synchronize_session=False)
        decks=Deck.query.filter(Deck.user_id.in_(user_ids)).all()
        deck_ids=[deck.id for deck in decks]
        if deck_ids:
            DeckCard.query.filter(DeckCard.deck_id.in_(deck_ids)).delete(synchronize_session=False)
            Deck.query.filter(Deck.id.in_(deck_ids)).delete(synchronize_session=False)
        UserCard.query.filter(UserCard.user_id.in_(user_ids)).delete(synchronize_session=False)
        User.query.filter(User.id.in_(user_ids)).delete(synchronize_session=False)
        db.session.commit()

@pytest.fixture(autouse=True)
def cleanup_selenium_data():
    cleanup_test_users()
    yield
    cleanup_test_users()
