from flask_login import current_user

def register_context_processors(app):
    @app.context_processor
    def inject_trade_notifications():
        from app.models import Trade

        if not current_user.is_authenticated:
            return {"has_unseen_trades": False}

        has_unseen_trades = Trade.query.filter_by(
            receiver_id=current_user.id,
            receiver_viewed=False
        ).first() is not None

        return {"has_unseen_trades": has_unseen_trades}
