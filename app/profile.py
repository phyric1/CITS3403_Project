from flask import render_template, abort, request, url_for, session, redirect, flash, Blueprint, current_app as app
from flask_login import login_user,logout_user,login_required,current_user
from app import db
from sqlalchemy import or_
from app.models import User, UserCard, Deck, DeckCard, Trade
from app.utils import get_user_deck, get_deck_cards
from app.utils import add_user_cards
from cards_logic import PlayerDeck
import os
from werkzeug.utils import secure_filename

bp = Blueprint("profile", __name__)

allowed_extensions = {"png", "jpg", "jpeg", "gif"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

@bp.route("/profile/<username>")
@login_required
def profile(username):
    user = db.session.query(User).filter_by(username=username).first()

    if user is None:
        abort(404)

    is_owner=current_user.id == user.id
    cards_collected=(db.session.query(UserCard).filter_by(user_id=user.id).count())
    active_trades=(db.session.query(Trade).filter(or_(Trade.sender_id==user.id, Trade.receiver_id==user.id)).count())
    deck=Deck.query.filter_by(user_id=user.id).first()
    if  deck:
        deck_size=DeckCard.query.filter_by(deck_id=deck.id).count()
    else:
        deck_size=0

    player={
        "username":user.username,
        "gold":user.gold,
        "easy_tokens":user.easy_tokens,
        "medium_tokens":user.medium_tokens,
        "hard_tokens":user.hard_tokens,
        "fastest_time":"N/A", #placeholder
        "total_runs":"N/A", #placeholder
        "dungeons_cleared":"N/A", #placeholder
        "cards_collected":cards_collected,
        "deck_size":deck_size,
        "active_trades":active_trades,
        "profile_photo":user.profile_photo or "default.png"
    }
    return render_template("profile.html", player=player, username=username, is_owner=is_owner)

@bp.route("/profile/<username>/photo", methods=["POST"])
@login_required
def upload_profile_photo(username):
    user=db.session.query(User).filter_by(username=username).first()
    if user is None:
        abort(404)
    if current_user.id != user.id:
        abort(403)
    file=request.files.get("profile_photo")

    if not file or file.filename=="":
        flash("No profile photo selected.", "warning")
        return redirect(url_for("profile.profile",username=username))
    if not allowed_file(file.filename):
        flash("Invalid file type. Please upload png,jpg,jpeg or gif.","danger")
        return redirect(url_for("profile.profile",username=username))
    filename=secure_filename(file.filename)
    extension=filename.rsplit(".",1)[1].lower()
    new_filename=f"user_{user.id}.{extension}"
    upload_folder=os.path.join(app.root_path,"static","profile_photo")
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, new_filename))
    user.profile_photo=new_filename
    db.session.commit()

    flash("Profile photo updated successfully","success")
    return redirect(url_for("profile.profile",username=username))

