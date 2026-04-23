from flask import render_template
from app import app
from app.forms import LoginForm, RegisterForm
from procedural_dungeon import generate_dungeon


@app.route("/")
@app.route("/index")
def index():
    return "Hello, World!"


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", title="Sign In", form=form)


@app.route("/register")
def register():
    form = RegisterForm()
    return render_template("register.html", title="Register", form=form)


@app.route("/game")
def game():
    return render_template("game.html", grid=generate_dungeon())


@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")


@app.route("/profile")
def profile():
    return "Profile page"
