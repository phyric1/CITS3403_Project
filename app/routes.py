from flask import render_template, request, url_for, redirect, flash, jsonify, Blueprint, current_app as app
from flask_login import login_user,logout_user,login_required,current_user
from app import db
from app.models import LifeTimeStats, User, Card, Game, GameStats
from app.forms import LoginForm, RegisterForm, ResetPasswordForm
from sqlalchemy import desc, case
from app.enums import CardType
from game_logic import DungeonGame
from app.utils import get_deck_cards
from app.utils import add_user_cards
from cards_logic import PlayerDeck
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
    if not existingGame:
        return jsonify({"error": "No active game"}), 404
    dungeon_game = existingGame.game
    data = request.get_json(silent=True) or {}
    input = data.get("input")
    output = dungeon_game.advance_game(input)
    existingGame.game = dungeon_game
    flag_modified(existingGame, "game")
    if dungeon_game.isGameOver:
        user = current_user
        if dungeon_game.isWin:
            user.gold += dungeon_game.player.gold
            if dungeon_game.difficulty == "Easy":
                user.common_tokens += 1
            elif dungeon_game.difficulty == "Normal":
                user.uncommon_tokens += 1
            elif dungeon_game.difficulty == "Hard":
                user.rare_tokens += 1
        game_stats = GameStats(
            user_id=current_user.id,
            difficulty=dungeon_game.difficulty,
            success=dungeon_game.isWin,
            turns=dungeon_game.gameOverStats["turnsPlayed"],
            gold_collected=dungeon_game.gameOverStats["goldCollected"],
            enemies_defeated=dungeon_game.gameOverStats["enemiesDefeated"],
            movement_cards_played=getattr(dungeon_game.playerDeck, 'movement_counter', 0),
            survival_cards_played=getattr(dungeon_game.playerDeck, 'survival_counter', 0),
            combat_cards_played=getattr(dungeon_game.playerDeck, 'combat_counter', 0),
            utility_cards_played=getattr(dungeon_game.playerDeck, 'utility_counter', 0),
        )

        lifetime_stats = current_user.lifetime_stats
        if not lifetime_stats:
            flash("Lifetime stats table could not be found.", "danger")
            return jsonify({"error": "Stats missing"}), 500

        lifetime_stats.games_played += 1
        if dungeon_game.isWin:
            lifetime_stats.wins += 1
            if (lifetime_stats.fastest_win_turns is None) or (lifetime_stats.fastest_win_turns > dungeon_game.gameOverStats["turnsPlayed"]):
                lifetime_stats.fastest_win_turns = dungeon_game.gameOverStats["turnsPlayed"]
        else:
            lifetime_stats.losses += 1
        lifetime_stats.turns += dungeon_game.gameOverStats["turnsPlayed"]
        lifetime_stats.gold_collected += dungeon_game.gameOverStats["goldCollected"]
        lifetime_stats.enemies_defeated  += dungeon_game.gameOverStats["enemiesDefeated"]
        lifetime_stats.movement_cards_played += getattr(dungeon_game.playerDeck, 'movement_counter', 0)
        lifetime_stats.survival_cards_played += getattr(dungeon_game.playerDeck, 'survival_counter', 0)
        lifetime_stats.combat_cards_played += getattr(dungeon_game.playerDeck, 'combat_counter', 0)
        lifetime_stats.utility_cards_played += getattr(dungeon_game.playerDeck, 'utility_counter', 0)
        lifetime_stats.score = (
            (lifetime_stats.wins * 500)
            + (lifetime_stats.gold_collected * 2)
            + (lifetime_stats.enemies_defeated * 25)
            + lifetime_stats.turns
            + (lifetime_stats.games_played * 50)
            - (lifetime_stats.losses * 100)
        )

        db.session.add(game_stats)
        db.session.delete(existingGame)
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
    page = request.args.get("page", 1, type=int)
    per_page = 25
    sort = request.args.get("sort", "score")

    win_rate = (
        LifeTimeStats.wins /
        case(
            (LifeTimeStats.games_played == 0, 1),
            else_=LifeTimeStats.games_played
        )
    )

    sort_options = {
        "score": desc(LifeTimeStats.score),
        "wins": desc(LifeTimeStats.wins),
        "losses": desc(LifeTimeStats.losses),
        "win_rate": desc(win_rate),
        "games_played": desc(LifeTimeStats.games_played),
        "turns": desc(LifeTimeStats.turns),
        "gold_collected": desc(LifeTimeStats.gold_collected),
        "enemies_defeated": desc(LifeTimeStats.enemies_defeated),
        "fastest_win_turns": LifeTimeStats.fastest_win_turns,
        "movement_cards_played": desc(LifeTimeStats.movement_cards_played),
        "survival_cards_played": desc(LifeTimeStats.survival_cards_played),
        "combat_cards_played": desc(LifeTimeStats.combat_cards_played),
        "utility_cards_played": desc(LifeTimeStats.utility_cards_played),
        "username": User.username
    }

    if sort not in sort_options:
        sort = "score"

    pagination = (
        LifeTimeStats.query
        .join(User, User.id == LifeTimeStats.user_id)
        .add_columns(win_rate.label("win_rate"))
        .order_by(sort_options[sort])
        .paginate(page=page, per_page=25, error_out=False)
    )

    entries = []
    for index, stats in enumerate(pagination.items, start=((page - 1) * per_page) + 1):
        entries.append({
            "ranking": index,
            "username": stats.user.username,
            "score": stats.score,
            "wins": stats.wins,
            "losses": stats.losses,
            "win_rate": (
                stats.wins / stats.games_played
                if stats.games_played else 0
            ),
            "games_played": stats.games_played,
            "turns": stats.turns,
            "gold_collected": stats.gold_collected,
            "enemies_defeated": stats.enemies_defeated,
            "fastest_win_turns": stats.fastest_win_turns,
            "movement_cards_played": stats.movement_cards_played,
            "survival_cards_played": stats.survival_cards_played,
            "combat_cards_played": stats.combat_cards_played,
            "utility_cards_played": stats.utility_cards_played,
        })

    return render_template("leaderboard.html", entries = entries, sort=sort)


@bp.route("/cards")
@login_required
def show_cards():
    cards = db.session.query(Card).filter(Card.type != CardType.debuff).all()

    return render_template("cards.html", cards=cards)
