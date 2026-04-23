from flask import render_template

from app import app
from app.forms import LoginForm, RegisterForm


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
    return "Game page"


@app.route("/leaderboard")
def leaderboard():
    return "Leaderboard page"


@app.route("/profile")
def profile():
    return "Profile page"
