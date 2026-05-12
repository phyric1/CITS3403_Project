from flask import render_template, abort, request, url_for, session, redirect, Blueprint
from flask_login import login_required, current_user
from app import db
from app.models import User, Card, UserCard, Trade, TradeCard
from app.enums import TradeStatus


bp = Blueprint("trading", __name__)

### TRADING RELATED ROUTES ###


@bp.route("/trading")
@login_required
def trading():
    current_user_id=current_user.id

    incoming_trade_rows = Trade.query.filter_by(receiver_id=current_user_id).order_by(Trade.creation_date.desc()).all()
    outgoing_trade_rows = Trade.query.filter_by(sender_id=current_user_id).order_by(Trade.creation_date.desc()).all()

    incoming_trades = []
    for trade in incoming_trade_rows:
        cards_requested = sum(1 for tc in trade.trade_cards if tc.user_card.user_id == trade.receiver_id)
        cards_offered = sum(1 for tc in trade.trade_cards if tc.user_card.user_id == trade.sender_id)

        incoming_trades.append({
            "id": trade.id,
            "from_user": trade.sender.username,
            "created_at": trade.creation_date.strftime("%Y-%m-%d"),
            "cards_requested": cards_requested,
            "cards_offered": cards_offered,
            "status": trade.status.value
        })

    outgoing_trades = []
    for trade in outgoing_trade_rows:
        cards_requested = sum(1 for tc in trade.trade_cards if tc.user_card.user_id == trade.receiver_id)
        cards_offered = sum(1 for tc in trade.trade_cards if tc.user_card.user_id == trade.sender_id)

        outgoing_trades.append({
            "id": trade.id,
            "to_user": trade.receiver.username,
            "created_at": trade.creation_date.strftime("%Y-%m-%d"),
            "cards_requested": cards_requested,
            "cards_offered": cards_offered,
            "status": trade.status.value
        })

    return render_template("trading/trading.html", incoming_trades=incoming_trades, outgoing_trades=outgoing_trades)



@bp.route("/trading/new")
@login_required
def new_trade():
    user = current_user

    target_username = request.args.get("target_username", "").strip()
    error = None
    target_user = None

    previous_target_username = session.get("trade_target_username")

    if not target_username:
        session.pop("requested_card_ids", None)
        session.pop("offered_card_ids", None)
        session.pop("trade_target_username", None)
    elif target_username != previous_target_username:
        session.pop("requested_card_ids", None)
        session.pop("offered_card_ids", None)
        session["trade_target_username"] = target_username
    else:
        session["trade_target_username"] = target_username

    if target_username:
        target_user = User.query.filter_by(username=target_username).first()

        if target_user is None:
            error = "User not found."
        elif target_user.id == user.id:
            error = "You cannot trade with yourself."
            target_user = None

    target_page = request.args.get("target_page", 1, type=int)
    my_page = request.args.get("my_page", 1, type=int)

    my_card_query = db.session.query(UserCard).join(Card).filter(UserCard.user_id == user.id, UserCard.tradable == True, UserCard.locked == False).order_by(Card.name)

    my_pagination = my_card_query.paginate(page=my_page, per_page=6, error_out=False)
    my_cards = my_pagination.items

    if target_user:
        target_card_query = db.session.query(UserCard).join(Card).filter(UserCard.user_id == target_user.id, UserCard.tradable == True, UserCard.locked == False).order_by(Card.name)

        target_pagination = target_card_query.paginate(page=target_page, per_page=6, error_out=False)
        target_cards = target_pagination.items
    else:
        target_pagination = None
        target_cards = []

    requested_card_ids = session.get("requested_card_ids", [])
    offered_card_ids = session.get("offered_card_ids", [])

    requested_cards = UserCard.query.filter(UserCard.id.in_(requested_card_ids)).all() if requested_card_ids else []
    offered_cards = UserCard.query.filter(UserCard.id.in_(offered_card_ids)).all() if offered_card_ids else []

    return render_template("trading/new_trade.html", target_user=target_user, target_username=target_username, target_cards=target_cards, requested_cards=requested_cards, offered_cards=offered_cards,
        my_cards=my_cards, target_pagination=target_pagination, my_pagination=my_pagination, requested_card_ids=requested_card_ids, offered_card_ids=offered_card_ids, error=error)



@bp.route("/trading/new/update-ajax", methods=["POST"])
@login_required
def update_trade_selection_ajax():

    data = request.get_json() or {}
    action = data.get("action")
    user_card_id = data.get("user_card_id")

    if not user_card_id:
        return {"success": False, "error": "Missing user_card_id"}, 400

    requested_card_ids = session.get("requested_card_ids", [])
    offered_card_ids = session.get("offered_card_ids", [])

    if action == "add_requested":
        if user_card_id not in requested_card_ids:
            requested_card_ids.append(user_card_id)
    elif action == "remove_requested":
        if user_card_id in requested_card_ids:
            requested_card_ids.remove(user_card_id)
    elif action == "add_offered":
        if user_card_id not in offered_card_ids:
            offered_card_ids.append(user_card_id)
    elif action == "remove_offered":
        if user_card_id in offered_card_ids:
            offered_card_ids.remove(user_card_id)
    else:
        return {"success": False, "error": "Invalid action"}, 400

    session["requested_card_ids"] = requested_card_ids
    session["offered_card_ids"] = offered_card_ids

    requested_cards = UserCard.query.filter(UserCard.id.in_(requested_card_ids)).all() if requested_card_ids else []
    offered_cards = UserCard.query.filter(UserCard.id.in_(offered_card_ids)).all() if offered_card_ids else []

    requested_html = render_template("trading/_trade_requested_cards.html", requested_cards=requested_cards)
    offered_html = render_template("trading/_trade_offered_cards.html", offered_cards=offered_cards)

    return {
        "success": True,
        "requested_count": len(requested_card_ids),
        "offered_count": len(offered_card_ids),
        "requested_html": requested_html,
        "offered_html": offered_html,
    }




@bp.route("/trading/new/submit", methods=["POST"])
@login_required
def submit_trade():
    sender_id = current_user.id
    target_username = request.form.get("target_username", "").strip()

    if not target_username:
        return redirect(url_for(".new_trade"))

    receiver = User.query.filter_by(username=target_username).first()
    if receiver is None:
        abort(400)

    if receiver.id == sender_id:
        abort(400)

    requested_card_ids = session.get("requested_card_ids", [])
    offered_card_ids = session.get("offered_card_ids", [])

    requested_cards = UserCard.query.filter(UserCard.id.in_(requested_card_ids), UserCard.user_id == receiver.id,UserCard.tradable==True,UserCard.locked==False).all() if requested_card_ids else []

    offered_cards = UserCard.query.filter(UserCard.id.in_(offered_card_ids), UserCard.user_id == sender_id,UserCard.tradable==True,UserCard.locked==False).all() if offered_card_ids else []

    if not requested_cards and not offered_cards:
        return redirect(url_for(".new_trade", target_username=target_username))

    trade = Trade(sender_id=sender_id, receiver_id=receiver.id, status=TradeStatus.pending)
    db.session.add(trade)
    db.session.flush()

    for card in requested_cards:
        card.locked = True
        db.session.add(TradeCard(trade_id=trade.id, user_card_id=card.id))

    for card in offered_cards:
        card.locked = True
        db.session.add(TradeCard(trade_id=trade.id, user_card_id=card.id))
    db.session.commit()

    session.pop("requested_card_ids", None)
    session.pop("offered_card_ids", None)

    return redirect(url_for(".trading"))



@bp.route("/trading/<int:trade_id>")
@login_required
def view_trade(trade_id):
    trade_row = db.session.get(Trade, trade_id)
    if trade_row is None:
        return redirect(url_for(".trading"))

    current_user_id = current_user.id
    if current_user_id not in [trade_row.sender_id, trade_row.receiver_id]:
        return redirect(url_for(".trading"))

    offered_cards = []
    requested_cards = []

    for trade_card in trade_row.trade_cards:
        if trade_card.user_card.user_id == trade_row.sender_id:
            offered_cards.append(trade_card.user_card)
        elif trade_card.user_card.user_id == trade_row.receiver_id:
            requested_cards.append(trade_card.user_card)

    trade = {"id": trade_row.id, "from_user": trade_row.sender.username, "to_user": trade_row.receiver.username, "created_at": trade_row.creation_date.strftime("%Y-%m-%d"), "status": trade_row.status.value,
        "offered_cards": offered_cards, "requested_cards": requested_cards}

    is_sender = current_user_id == trade_row.sender_id
    is_receiver = current_user_id == trade_row.receiver_id

    return render_template("trading/view_trade.html", trade=trade, is_sender=is_sender, is_receiver=is_receiver)



@bp.route("/trading/<int:trade_id>/action", methods=["POST"])
@login_required
def trade_action(trade_id):

    current_user_id = current_user.id
    trade = db.session.get(Trade, trade_id)

    if trade is None:
        return redirect(url_for(".trading"))

    action = request.form.get("action")

    if current_user_id not in [trade.sender_id, trade.receiver_id]:
        return redirect(url_for(".trading"))

    if action == "accept":
        if current_user_id != trade.receiver_id:
            return redirect(url_for(".trading"))

        for trade_card in trade.trade_cards:
            user_card = trade_card.user_card
            if user_card.user_id == trade.sender_id:
                user_card.user_id = trade.receiver_id
            elif user_card.user_id == trade.receiver_id:
                user_card.user_id = trade.sender_id
            user_card.locked = False

        db.session.delete(trade)
        db.session.commit()

    elif action == "reject":
        if current_user_id != trade.receiver_id:
            return redirect(url_for(".trading"))

        for trade_card in trade.trade_cards:
            trade_card.user_card.locked = False

        db.session.delete(trade)
        db.session.commit()

    elif action == "cancel":
        if current_user_id != trade.sender_id:
            return redirect(url_for(".trading"))

        for trade_card in trade.trade_cards:
            trade_card.user_card.locked = False

        db.session.delete(trade)
        db.session.commit()

    else:
        return redirect(url_for(".trading"))

    return redirect(url_for(".trading"))



"""
@bp.route("/market")
def trade_market():
    cards = db.session.query(Card).filter(Card.type != CardType.debuff).all()

    return render_template("trading/market.html", cards=cards)


@bp.route("/market/<int:card_id>")
def market_card(card_id):
    cards = db.session.query(UserCard).filter(UserCard.card_id == card_id).all()

    return render_template("trading/trade_market.html", cards=cards)
"""
### ### ### ### ### ### ###