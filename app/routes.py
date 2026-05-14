from flask import render_template, abort, request, url_for, session, redirect, flash, jsonify, Blueprint, current_app as app
from flask_login import login_user,logout_user,login_required,current_user
from app import db
from sqlalchemy import case
from app.models import User, Card, UserCard, Deck, DeckCard, Trade, TradeCard, Game
from app.forms import LoginForm, RegisterForm
from sqlalchemy import case, func, or_
from app.models import User, Card, UserCard, Deck, DeckCard, Trade, TradeCard
from app.forms import LoginForm, RegisterForm, ResetPasswordForm
from app.enums import TradeStatus, CardRarity, CardType
from game_logic import DungeonGame, Player, Grid
from app.utils import get_user_deck, get_deck_cards
from app.utils import add_user_cards
from cards_logic import PlayerDeck
import random
from datetime import date
from types import SimpleNamespace
from sqlalchemy.orm.attributes import flag_modified

bp = Blueprint("main", __name__)
@bp.route("/")
@bp.route("/index")
def index():
    return render_template("landing.html")


@bp.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile.profile", username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user=db.session.query(User).filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.", "danger")
        else:
            login_user(user)
            return redirect(url_for("profile.profile", username=user.username))

    return render_template("login.html",title="Login", form=form)

@bp.route("/reset-password",methods=["GET","POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for("profile.profile", username=current_user.username))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        user=db.session.query(User).filter_by(username=form.username.data,email=form.email.data).first()
        if user is None:
            flash("Invalid username or email","danger")
            return redirect(url_for("main.reset_password"))
        user.set_password(form.new_password.data)
        db.session.commit()
        flash("Password reser successfully. Please log in with new password.","success")
        return redirect(url_for("main.login"))
    return render_template("reset_password.html",form=form)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@bp.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_username=db.session.query(User).filter_by(username=form.username.data).first()
        existing_email=db.session.query(User).filter_by(email=form.email.data).first()

        if existing_username:
            flash("Username is already taken.", "danger")
        elif existing_email:
            flash("Email is already registered.", "danger")
        else:
            user=User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()
            add_user_cards(user.id, [
                ("Silence Falls", 3),
                ("Tailwind", 3),
                ("Dagger", 3),
                ("Dexterity", 1),
                ("Rest", 2),
            ])
            db.session.commit()
            login_user(user)
            return redirect(url_for("profile.profile", username=user.username))

    return render_template("register.html", title="Register", form=form)

@bp.route("/start", methods=["POST"])
@login_required
def start():
    if not current_user.id:
        return redirect(url_for("main.login"))
    existingGame = Game.query.filter_by(user_id = current_user.id).first()
    if not existingGame: #create new game
        difficulty = request.json.get("difficulty")
        dungeon_game = DungeonGame(difficulty)
        dungeon_game.playerDeck = PlayerDeck()
        dungeon_game.playerDeck.deck = get_deck_cards(current_user.id)
        dungeon_game.playerDeck.loadDeck()
        dungeon_game.hand = dungeon_game.playerDeck.shuffle(dungeon_game.playerDeck.deck)
        game = Game(user_id = current_user.id, game = dungeon_game)
        db.session.add(game)
        db.session.commit()
    return redirect(url_for("main.game"))

@bp.route("/game")
@login_required
def game():
    if not current_user.id:
        return redirect(url_for("main.login"))
    existingGame = Game.query.filter_by(user_id = current_user.id).first()
    if existingGame:
        return render_template("game.html")
    else:
        return render_template("start_game.html")

@bp.route("/game/state")
@login_required
def game_state():
    existingGame = Game.query.filter_by(user_id = current_user.id).first()
    if not existingGame:
        return jsonify({"error": "No active game"}), 404
    dungeon_game = existingGame.game
    return dungeon_game.displayGame()

@bp.route("/move", methods=["POST"])
@login_required
def move():
    if not current_user.id:
        return redirect(url_for("main.login"))
    existingGame = Game.query.filter_by(user_id = current_user.id).first()
    dungeon_game = existingGame.game
    input = request.json.get("input")
     #change to input data
    output = dungeon_game.advance_game(input)
    existingGame.game = dungeon_game
    flag_modified(existingGame, "game")
    db.session.commit()
    return output

@bp.route("/reset", methods=["POST"])
@login_required
def reset():
    existingGame = Game.query.filter_by(user_id = current_user.id).first()
    if existingGame:
        db.session.delete(existingGame)
        db.session.commit()
    return redirect(url_for("main.game"))

@bp.route("/leaderboard")
def leaderboard():
    players = [
        {"ranking": 1, "player": "player1", "stat1": 70, "stat2": 20},
        {"ranking": 2, "player": "player2", "stat1": 31, "stat2": 30},
        {"ranking": 3, "player": "player3", "stat1": 35, "stat2": 10},
        {"ranking": 4, "player": "player4", "stat1": 35, "stat2": 10},       # ranking will probably be determined by combination of stats in the future
        {"ranking": 5, "player": "player5", "stat1": 21, "stat2": 40},
        {"ranking": 6, "player": "player6", "stat1": 65, "stat2": 60},
    ]

    sort = request.args.get("sort")

    if sort == "ranking":
        players = sorted(players, key=lambda x: x["ranking"])
    elif sort == "player":
        players = sorted(players, key=lambda x: x["player"].lower())
    elif sort == "stat1":
        players = sorted(players, key=lambda x: x["stat1"], reverse=True)
    elif sort == "stat2":
        players = sorted(players, key=lambda x: x["stat2"], reverse=True)
    else:
        sort = "ranking"
        players = sorted(players, key=lambda x: x["ranking"])


    return render_template("leaderboard.html", players = players, sort=sort)


@bp.route("/cards")
@login_required
def show_cards():
    cards = db.session.query(Card).filter(Card.type != CardType.debuff).all()

    return render_template("cards.html", cards=cards)
