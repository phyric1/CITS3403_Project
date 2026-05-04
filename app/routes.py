from flask import render_template, abort, request, url_for, session, redirect, Blueprint, current_app as app
from app import db
from app.models import User, Card, UserCard, Deck, DeckCard
from app.enums import TradeStatus, CardRarity, CardType
from game_logic import DungeonGame, Player, Grid
from app.utils import add_user_cards

bp = Blueprint("main", __name__)
dungeon_game = DungeonGame()

@bp.route("/")
@bp.route("/index")
def index():
    return render_template("landing.html")


@bp.route("/login",methods=["GET","POST"])
def login():
    errors={}
    if request.method=="POST":
        username=request.form.get("username","").strip()
        password=request.form.get("password","")

        if not username:
            errors["username"]="Username is required."
        if not password:
            errors["password"]="Password is required."
        if not errors:
            user=db.session.query(User).filter_by(username=username).first()
            if user is None:
                errors["general"]="Invalid username or password."
            elif not user.check_password(password):
                errors["general"]="Invalid username or password."
            else:
                session["user_id"]=user.id
                session["username"]=user.username
                return redirect(url_for("main.index"))

    return render_template("login.html",title="Login",errors=errors)


@bp.route("/logout")
def logout():
    session.pop("user_id",None)
    session.pop("username",None)
    return redirect(url_for("main.index"))

@bp.route("/register",methods=["GET","POST"])
def register():
    errors={}
    success=session.pop("register_success",False)
    if request.method=="POST":
        username=request.form.get("username","").strip()
        email=request.form.get("email","").strip().lower()
        password=request.form.get("password","")
        confirm_password=request.form.get("confirm_password","")

        if not username:
            errors["username"]="Username is required."

        if not email:
            errors["email"]="Email is required."
        elif "@" not in email or "." not in email:
            errors["email"]="Please enter a valid email address."

        if not password:
            errors["password"]="Password is required."
        elif len(password)<8:
            errors["password"]="Password must be at least 8 characters"

        if not confirm_password:
            errors["confirm_password"]="Please confirm your password."
        elif password != confirm_password:
            errors["confirm_password"]="Passwords do not match."

        #Check whether the username and email already exist.
        if not errors:
            existing_username=db.session.query(User).filter_by(username=username).first()
            existing_emial=db.session.query(User).filter_by(email=email).first()

            if existing_username:
                errors["username"]="This username is already taken."

            if existing_emial:
                errors["email"]="This email is already registered."

        if not errors:
            user=User(username=username,email=email)
            user.set_password(password)
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
            session["register_success"]=True
            return redirect(url_for("main.register"))

    return render_template("register.html",title="Register",errors=errors,success=success)


@bp.route("/game")
def game():
    fake_data = { # TODO: Change to real query
        "phyric1": [
            {
                "card": {
                    "name": "Tailwind",
                    "effect": "Move 2 Spaces without triggering enemy behavior",
                    "type": type("Enum", (), {"value": "movement"})(),
                    "rarity": type("Enum", (), {"value": "common"})(),
                    "max": 7,
                    "uses": 7,
                },
                "uses_remaining": 5,
            },
            {
                "card": {
                    "name": "Heal",
                    "effect": "Heals 2 Hearts / Adds 2 Hearts",
                    "type": type("Enum", (), {"value": "survival"})(),
                    "rarity": type("Enum", (), {"value": "rare"})(),
                    "max": 5,
                    "uses": 5,
                },
                "uses_remaining": 2,
            },
            {
                "card": {
                    "name": "Silence Falls",
                    "effect": "Stealth +1",
                    "type": type("Enum", (), {"value": "utility"})(),
                    "rarity": type("Enum", (), {"value": "common"})(),
                    "max": 7,
                    "uses": 7,
                },
                "uses_remaining": -1,
            },
        ]
    }
    items = fake_data.get("phyric1")

    return render_template("game.html", grid=dungeon_game.getFakeGrid(), items=items)

@bp.route("/move", methods=["POST"])
def move():
    direction = request.json.get("direction")
    return dungeon_game.advance_game(direction)

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
def profile(username):
    user = db.session.query(User).filter_by(username=username).first()

    if user is None:
        abort(404)

    player={
            "username": user.username,
            "gold": 120,
            "fastest_time": 3.55,
            "total_runs": 10,
            "dungeons_cleared": 8,
            "cards_collected": 10,
            "deck_size": 4,
            "trade_completed": 3,
            "favourite_card": "Tailwind"
        }

    return render_template("profile.html",player=player, username=username)


@bp.route("/trading")
def trading():


    incoming_trades = [{"id": 1, "from_user": "player2", "created_at": "2026-05-01", "cards_requested": 2, "cards_offered": 1}]
    outgoing_trades = [{"id": 2, "to_user": "player2", "created_at": "2026-05-01", "cards_requested": 1, "cards_offered": 1}]
    return render_template("trading.html", incoming_trades=incoming_trades, outgoing_trades=outgoing_trades)


@bp.route("/trading/new")
def new_trade():


    return render_template("new_trade.html")



@bp.route("/trading/<int:trade_id>")
def view_trade(trade_id):


    hardcoded_trades = {
        1: {"id": 1, "from_user": "player2", "to_user": "player1", "created_at": "2026-05-01", "status": "Pending",
            "offered_cards": [{"name": "Tailwind", "effect": "Move 2 Spaces without triggering enemy behavior", "type": "movement", "rarity": "common", "max": 7, "count": 1}],
            "requested_cards": [{"name": "Dynamite", "effect": "Deals damage in a 5x5 radius, -2 stealth", "type": "combat", "rarity": "rare", "max": 3, "count": 1},
                                {"name": "Heal", "effect": "Heals 2 Hearts / Adds 2 Hearts", "type": "survival", "rarity": "rare", "max": 5, "count": 1}]},

        2: {"id": 2, "from_user": "player1", "to_user": "player2", "created_at": "2026-05-01", "status": "Pending",
            "offered_cards": [{"name": "Heal", "effect": "Heals 2 Hearts / Adds 2 Hearts", "type": "survival", "rarity": "rare", "max": 5, "count": 1}],
            "requested_cards": [{"name": "Tailwind", "effect": "Move 2 Spaces without triggering enemy behavior", "type": "movement", "rarity": "common", "max": 7, "count": 1}]}
    }

    trade = hardcoded_trades.get(trade_id)

    if trade is None:
        abort(404)

    return render_template("view_trade.html", trade=trade)
