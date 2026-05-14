from flask import render_template, abort, request, url_for, session, redirect, flash, Blueprint, current_app as app
from flask_login import login_user,logout_user,login_required,current_user
from app import db
from sqlalchemy import case
from app.models import User, Card, UserCard, Deck, DeckCard, Trade, TradeCard
from app.forms import LoginForm, RegisterForm
from app.enums import TradeStatus, CardRarity, CardType
from game_logic import DungeonGame, Player, Grid
from app.utils import get_user_deck, get_deck_cards
from app.utils import add_user_cards
from cards_logic import PlayerDeck
import random
from datetime import date
from types import SimpleNamespace

bp = Blueprint("main", __name__)
dungeon_game = DungeonGame()
@bp.route("/")
@bp.route("/index")
def index():
    return render_template("landing.html")


@bp.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile", username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user=db.session.query(User).filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.", "danger")
        else:
            login_user(user)
            return redirect(url_for("main.profile", username=user.username))

    return render_template("login.html",title="Login", form=form)


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
            return redirect(url_for("main.profile", username=user.username))

    return render_template("register.html", title="Register", form=form)

@bp.route("/game")
@login_required
def game():
    TILE_CLASSES = {
        -1: "dark",
        0: "floor",
        1: "wall",
        2: "start",
        3: "end",
        4: "enemy",
        5: "key",
        6: "exit",
        7: "gold",
    }

    if not current_user.id:
        return redirect(url_for("main.login"))
    dungeon_game.playerDeck = PlayerDeck()
    dungeon_game.playerDeck.deck = get_deck_cards(current_user.id)
    dungeon_game.playerDeck.loadDeck()
    dungeon_game.hand = dungeon_game.playerDeck.shuffle(dungeon_game.playerDeck.deck)
    return render_template("game.html", grid=dungeon_game.getFakeGrid(), TILE_CLASSES=TILE_CLASSES)

@bp.route("/move", methods=["POST"])
@login_required
def move():
    if not current_user.id:
        return redirect(url_for("main.login"))

    input = request.json.get("input") #change to input data
    return dungeon_game.advance_game(input)

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


@bp.route("/profile/<username>")
@login_required
def profile(username):
    user = db.session.query(User).filter_by(username=username).first()

    if user is None:
        abort(404)

    player={
            "username": user.username,
            "gold": user.gold,
            "fastest_time": 3.55,
            "total_runs": 10,
            "dungeons_cleared": 8,
            "cards_collected": 10,
            "deck_size": 4,
            "trade_completed": 3,
            "favourite_card": "Tailwind"
        }

    return render_template("profile.html",player=player, username=username)

@bp.route("/cards")
@login_required
def show_cards():
    cards = db.session.query(Card).filter(Card.type != CardType.debuff).all()

    return render_template("cards.html", cards=cards)
