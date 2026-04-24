from flask import render_template
from app import app
from procedural_dungeon import generate_dungeon

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
    return render_template("game.html", grid=generate_dungeon())


@app.route("/leaderboard")
def leaderboard():
    players = [
        {"ranking": 1, "player": "player1", "stat1": 40, "stat2": 20},
        {"ranking": 2, "player": "player2", "stat1": 40, "stat2": 30},
        {"ranking": 3, "player": "player3", "stat1": 35, "stat2": 10},
    ]
    return render_template("leaderboard.html", players = players)


@app.route("/profile")
def profile():
    return "Profile page"
