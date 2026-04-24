from flask import render_template, abort

from app import app


@app.route("/")
@app.route("/index")
def index():
    return "Hello, World!"


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/game")
def game():
    return "Game page"


@app.route("/leaderboard")
def leaderboard():
    return "Leaderboard page"


@app.route("/profile")
def profile():
    return "Profile page"


@app.route("/profile/<username>/inventory")
def inventory(username):
    fake_data = { # Remove when database is implemented
        "phyric1": [
            {"name": "Tailwind", "effect": "Move 2 Spaces without triggering enemy behavior", "type": "movement", "rarity": "common", "max": 7},
            {"name": "Silence Falls", "effect": "Stealth +1", "type": "utility", "rarity": "common", "max": 7},
            {"name": "Dynamite", "effect": "Deals damage in 5x5 radius, -2 stealth points blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah  blah blah blah blah blah blah blah blah blah", "type": "combat", "rarity": "rare", "max": 3},
        ]
    }

    items = fake_data.get(username)
    if items is None:
        abort(404)  # user not found
    return render_template("inventory.html", items=items, username=username)
