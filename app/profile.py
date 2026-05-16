from flask import render_template, abort, request, url_for, redirect, flash, Blueprint, current_app as app
from flask_login import login_required,current_user
from app import db
from sqlalchemy import or_, case
from app.models import User, UserCard, Deck, DeckCard, Trade, GameStats, LifeTimeStats
import os
from werkzeug.utils import secure_filename

from app.routes import game

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

    lifetime_stats = user.lifetime_stats
    games = (
        db.session.query(GameStats)
        .filter(GameStats.user_id == user.id)
        .order_by(GameStats.init_at.asc())
        .limit(10)
        .all()
    )
    difficulty_map = {"easy": 0, "normal": 1, "hard": 2}

    game_data = {
        "labels": [f"Game {i+1}" for i in range(len(games))],
        "score": [g.score for g in games],
        "turns": [g.turns for g in games],
        "gold": [g.gold_collected for g in games],
        "enemies": [g.enemies_defeated for g in games],
        "movement": [g.movement_cards_played for g in games],
        "survival": [g.survival_cards_played for g in games],
        "combat": [g.combat_cards_played for g in games],
        "utility": [g.utility_cards_played for g in games],
        "wins": [1 if g.success else 0 for g in games],
        "difficulty": [difficulty_map.get(g.difficulty.lower(), 0) for g in games]
    }

    win_rate = 0 if lifetime_stats.games_played == 0 else round(
        (lifetime_stats.wins / lifetime_stats.games_played) * 100,
        1
    )

    player={
        "username":user.username,
        "gold":user.gold,
        "common_tokens":user.common_tokens,
        "uncommon_tokens":user.uncommon_tokens,
        "rare_tokens":user.rare_tokens,
        "cards_collected":cards_collected,
        "deck_size":deck_size,

        "score": lifetime_stats.score,
        "wins": lifetime_stats.wins,
        "losses": lifetime_stats.losses,
        "win_rate": win_rate,
        "games_played": lifetime_stats.games_played,
        "turns": lifetime_stats.turns,
        "gold_collected": lifetime_stats.gold_collected,
        "enemies_defeated": lifetime_stats.enemies_defeated,
        "fastest_win_turns": lifetime_stats.fastest_win_turns,
        "movement_cards_played": lifetime_stats.movement_cards_played,
        "survival_cards_played": lifetime_stats.survival_cards_played,
        "combat_cards_played": lifetime_stats.combat_cards_played,
        "utility_cards_played": lifetime_stats.utility_cards_played,

        "active_trades":active_trades,
        "profile_photo":user.profile_photo or "default.png"
    }
    return render_template("profile.html", player=player, username=username, game_data=game_data, is_owner=is_owner)

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

    old_photo=user.profile_photo
    #delete old profile photo
    if old_photo and  old_photo != "default.png":
        old_photo_path=os.path.join(upload_folder,old_photo)
        if os.path.exists(old_photo_path):
            os.remove(old_photo_path)
    file.save(os.path.join(upload_folder, new_filename))
    user.profile_photo=new_filename
    db.session.commit()

    flash("Profile photo updated successfully","success")
    return redirect(url_for("profile.profile",username=username))
