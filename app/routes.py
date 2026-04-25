from flask import render_template, abort, request
from app import app
from procedural_dungeon import generate_dungeon

@app.route("/")
@app.route("/index")
def index():
    return render_template("landing.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/game")
def game():
    return render_template("game.html", grid=generate_dungeon())


@app.route("/leaderboard")
def leaderboard():
    players = [
        {"ranking": 1, "player": "player1", "stat1": 40, "stat2": 20},
        {"ranking": 2, "player": "player2", "stat1": 40, "stat2": 30},
        {"ranking": 3, "player": "player3", "stat1": 35, "stat2": 10},
    ]
    return render_template("leaderboard.html", players = players)


@app.route("/profile/<username>")
def profile(username):
    fake_profiles={ # TODO: Remove when database is implemented
        "phyric1":{
            "username":"phyric1",
            "gold":120,
            "fastest_time":3.55,
            "total_runs":10,
            "dungeons_cleared":8,
            "cards_collected":10,
            "deck_size":4,
            "trade_completed":3,
            "favourite_card":"Tailwind"
        }
    }
    player=fake_profiles.get(username)

    if player is None:
        abort(404)
    
    return render_template("profile.html",player=player, username=username)


@app.route("/profile/<username>/inventory")
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
