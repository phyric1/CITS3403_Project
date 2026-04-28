from flask import render_template, abort, request, url_for, session, redirect, Blueprint, current_app as app
from app import db
from app.models import User, Card, UserCard, Deck, DeckCard
from app.enums import TradeStatus, CardRarity, CardType
from game_logic import DungeonGame, Player, Grid

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
                return redirect(url_for("index"))

    return render_template("login.html",title="Login",errors=errors)


@bp.route("/logout")
def logout():
    session.pop("user_id",None)
    session.pop("username",None)
    return redirect(url_for("index"))

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
            db.session.commit()
            session["register_success"]=True
            return redirect(url_for("register"))

    return render_template("register.html",title="Register",errors=errors,success=success)


@bp.route("/game")
def game():
    fake_data = { # TODO: Remove when database is implemented
        "phyric1": [
            {"name": "Tailwind", "effect": "Move 2 Spaces without triggering enemy behavior", "type": "movement", "rarity": "common", "max": 7, "count": 3},
            {"name": "Heal", "effect": "Heals 2 Hearts / Adds 2 Hearts", "type": "survival", "rarity": "rare", "max": 5, "count": 1},
            {"name": "Silence Falls", "effect": "Stealth +1", "type": "utility", "rarity": "common", "max": 7, "count": 4},
        ]
    }
    items = fake_data.get("phyric1")

    return render_template("game.html", grid=dungeon_game.getGrid(), items=items)

@bp.route("/move", methods=["POST"])
def move():
    direction = request.json.get("direction")
    return dungeon_game.getPlayer().movePlayer(direction, dungeon_game)


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


@bp.route("/profile/<username>/inventory")
def inventory(username):
    fake_data = { # TODO: Remove when database is implemented
        "phyric1": [
            {"name": "Tailwind", "effect": "Move 2 Spaces without triggering enemy behavior", "type": "movement", "rarity": "common", "max": 7, "count": 3},
            {"name": "Heal", "effect": "Heals 2 Hearts / Adds 2 Hearts", "type": "survival", "rarity": "rare", "max": 5, "count": 1},
            {"name": "Silence Falls", "effect": "Stealth +1", "type": "utility", "rarity": "common", "max": 7, "count": 4},
            {"name": "Dynamite", "effect": "Deals damage in 5x5 radius, -2 stealth points blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah  blah blah blah blah blah blah blah blah blah", "type": "combat", "rarity": "epic", "max": 3, "count": 2},
        ]
    }

    items = fake_data.get(username)
    if items is None:
        abort(404)

    sort = request.args.get("sort")
    if sort == "name":
        items = sorted(items, key=lambda x: x["name"])
    elif sort == "rarity":
        rarity_order = {"common": 0, "rare": 1, "epic": 2, "legendary": 3, "master": 3}
        items = sorted(items, key=lambda x: rarity_order.get(x["rarity"], 0))
    elif sort == "type":
        items = sorted(items, key=lambda x: x["type"])
    elif sort == "max":
        items = sorted(items, key=lambda x: x["max"], reverse=True)
    return render_template("inventory.html", items=items, username=username)
