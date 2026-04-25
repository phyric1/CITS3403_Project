from flask import render_template, request, jsonify
from app import app
from procedural_dungeon import generate_dungeon

# Store game state globally (in production, use sessions)
game_state = {"grid": None, "player": None}


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
    global game_state
    grid, player = generate_dungeon()
    game_state = {"grid": grid, "player": player}
    return render_template("game.html", grid=grid, player=player)

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")


@app.route("/profile")
def profile():
    return "Profile page"
