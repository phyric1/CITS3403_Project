from flask import render_template, abort, request, url_for, session, redirect, Blueprint, current_app as app
from app import db
from sqlalchemy import case
from app.models import User, Card, UserCard, Deck, DeckCard, Trade, TradeCard
from app.enums import TradeStatus, CardRarity, CardType
from game_logic import DungeonGame, Player, Grid
from app.utils import add_user_cards
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





def get_daily_shop_cards(user_id):
    all_cards=db.session.query(Card).filter(Card.type != CardType.debuff).all()
    today=date.today().isoformat()
    #Different daily shops for each user
    random.seed(f"{today}-{user_id}")

    if len(all_cards) <= 4:
        return all_cards

    return random.sample(all_cards, 4)

def get_card_price(card):
    rarity=card.rarity.value
    price_rarity={
        "common": 20,
        "uncommon": 35,
        "rare": 60,
        "legendary": 120,
        "master": 200
    }
    return price_rarity.get(rarity,30)

def card_pack_probability(token_type):
    probabilities={
        "easy": {"common": 0.7, "uncommon": 0.2, "rare": 0.09, "legendary": 0.009, "master": 0.001},
        "medium": {"common": 0.5, "uncommon": 0.3, "rare": 0.15, "legendary": 0.045, "master": 0.005},
        "hard": {"common": 0.25, "uncommon": 0.4, "rare": 0.2, "legendary": 0.1, "master": 0.05}
    }
    if token_type not in probabilities:
        raise ValueError("Invalid token type.")
    
    return probabilities[token_type]

def get_type_value(card):
    card_type=card.type
    if hasattr(card_type, "value"):
        card_type=card_type.value

    return str(card_type).lower()

def get_rarity_value(card):
    rarity=card.rarity
    if hasattr(rarity, "value"):
        rarity=rarity.value

    return str(rarity).lower()

#sperate 2 card_pack and make sure at least 1 high vlaue card.
def random_cards(token_type):
    probabilities=card_pack_probability(token_type)
    all_cards=db.session.query(Card).filter(Card.type != CardType.debuff).all()
    guarantee_cards=[]
    guarantee_probability=[]
    normal_cards=[]
    normal_probability=[]
    for card in all_cards:
        rarity=get_rarity_value(card)
        probability=probabilities.get(rarity,0)
        if probability>0:
            normal_cards.append(card)
            normal_probability.append(probability)
            if rarity in ["uncommon", "rare", "legendary", "master"]:
                guarantee_cards.append(card)
                guarantee_probability.append(probability)
    if not normal_cards:
        return []
    
    cards=[]
    if guarantee_cards:
        guarantee_cards=random.choices(guarantee_cards,weights=guarantee_probability,k=1)[0]
        cards.append(guarantee_cards)
    
    count=3-len(cards)
    if count>0:
        cards.extend(random.choices(normal_cards,weights=normal_probability,k=count))
    
    return cards

@bp.route("/shop")
def shop():
    user=db.session.query(User).get(session.get("user_id"))
    daily_cards=get_daily_shop_cards(user.id)
    today=date.today().isoformat()
    purchase_key=f"daily_shop_purchases_{user.id}_{today}"
    purchase_card_id=session.get(purchase_key,[])

    shop_items=[]
    for card in daily_cards:
        shop_items.append(SimpleNamespace(card=card,uses_remaining=card.uses,is_purchased=card.id in purchase_card_id,price=get_card_price(card)))
    message=request.args.get("message")
    a_pack=session.pop("pack",None)
    pack=[]
    if a_pack:
        for card in a_pack:
            pack.append(SimpleNamespace(
                card=SimpleNamespace(
                    name=card["name"],
                    effect=card["effect"],
                    rarity=SimpleNamespace(value=card["rarity"]),
                    type=SimpleNamespace(value=card["type"]),
                    uses=card["uses"],
                    max=card["max"]
                ),
                uses_remaining=card["uses_remaining"]
            ))

    return render_template("shop.html",user=user,shop_items=shop_items,today=today,message=message,pack=pack)

@bp.route("/shop/buy/<int:card_id>", methods=["POST"])
def buy_card(card_id):
    user=db.session.query(User).get(session.get("user_id"))
    card=db.session.query(Card).get(card_id)

    if card is None:
        abort(404)

    daily_cards=get_daily_shop_cards(user.id)
    daily_cards_ids=[daily_card.id for daily_card in daily_cards]
    if card.id not in daily_cards_ids:
        return redirect(url_for("main.shop",message="This card is not available in Daily Shop"))

    today=date.today().isoformat()
    purchase_key=f"daily_shop_purchases_{user.id}_{today}"
    purchase_card_id=session.get(purchase_key,[])
    if card.id in purchase_card_id:
        return redirect(url_for("main.shop",message="You have buy this card today."))

    price=get_card_price(card)
    if user.gold<price:
        return redirect(url_for("main.shop", message="You don't have enough money"))
    user.gold-=price

    user_card=UserCard(user_id=user.id,card_id=card.id,uses_remaining=card.uses)
    db.session.add(user_card)
    db.session.commit()
    purchase_card_id.append(card.id)
    session[purchase_key]= purchase_card_id
    session.modified=True

    return redirect(url_for("main.shop",message="Card purchased successfully."))

@bp.route("/shop/open_pack/<token_type>", methods=["POST"])
def open_pack(token_type):
    user=db.session.query(User).get(session.get("user_id"))
    if token_type not in ["easy","medium","hard"]:
        abort(404)
    if token_type=="easy":
        if user.easy_tokens<=0:
            return redirect(url_for(".shop",message="You don't have enough easy tokens."))
    elif token_type=="medium":
        if user.medium_tokens<=0:
            return redirect(url_for(".shop",message="You don't have enough medium tokens."))
    elif token_type=="hard":
        if user.hard_tokens<=0:
            return redirect(url_for(".shop",message="You don't have enough hard tokens."))
    
    cards=random_cards(token_type)
    if not cards:
        return redirect(url_for(".shop",message="No cards available to open in this pack."))
    
    if token_type=="easy":
        user.easy_tokens-=1
    elif token_type=="medium":
        user.medium_tokens-=1
    elif token_type=="hard":
        user.hard_tokens-=1
    
    for card in cards:
        user_card=UserCard(user_id=user.id,card_id=card.id,uses_remaining=card.uses)
        db.session.add(user_card)

    pack=[]
    for card in cards:
        pack.append({"name":card.name,"effect":card.effect,"rarity":get_rarity_value(card),"type":get_type_value(card),"uses":card.uses,"max":card.max_in_deck,"uses_remaining":card.uses})
    session["pack"]=pack
    session.modified=True
    db.session.commit()
    return redirect(url_for(".shop",message=f"You have opened a {token_type} pack."))

@bp.route("/cards")
def show_cards():
    cards = db.session.query(Card).filter(Card.type != CardType.debuff).all()

    return render_template("cards.html", cards=cards)
