import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture()
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()

def make_user():
    suffix = str(int(time.time() * 1000))[-8:]
    username = f"selenium{suffix}"
    email = f"selenium{suffix}@test.com"
    password = "test1234"
    return username, email, password

def click_submit(driver):
    driver.find_element(By.CSS_SELECTOR, "input[type='submit'],button[type='submit']").click()

def register_user(driver):
    username, email, password = make_user()
    driver.get(f"{BASE_URL}/register")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confirm_password").send_keys(password)
    click_submit(driver)
    WebDriverWait(driver, 10).until(EC.url_contains("/profile/"))
    return username, email, password

def login_user(driver, username, password):
    driver.get(f"{BASE_URL}/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    click_submit(driver)
    WebDriverWait(driver, 10).until(EC.url_contains("/profile/"))

def logout_user(driver):
    driver.get(f"{BASE_URL}/logout")

def give_user_card_to_user(username, card_name, tradable=True, locked=False, uses_remaining=3):
    from app import create_app, db
    from app.models import User, Card, UserCard

    flask_app = create_app()
    with flask_app.app_context():
        user = User.query.filter_by(username=username).first()
        card = Card.query.filter_by(name=card_name).first()
        assert user is not None
        assert card is not None
        user_card = UserCard(
            user_id=user.id,
            card_id=card.id,
            tradable=tradable,
            locked=locked,
            uses_remaining=uses_remaining
        )
        db.session.add(user_card)
        db.session.commit()
        return user_card.id, card.id


def create_trade_between_users(sender_username, receiver_username):
    from app import create_app, db
    from app.models import User, UserCard, Trade, TradeCard
    flask_app = create_app()
    with flask_app.app_context():
        sender = User.query.filter_by(username=sender_username).first()
        receiver = User.query.filter_by(username=receiver_username).first()
        assert sender is not None
        assert receiver is not None

        sender_card = UserCard.query.filter_by(user_id=sender.id, locked=False).first()
        receiver_card = UserCard.query.filter_by(user_id=receiver.id, locked=False).first()
        assert sender_card is not None
        assert receiver_card is not None

        sender_card.locked = True
        receiver_card.locked = True
        trade = Trade(sender_id=sender.id, receiver_id=receiver.id, receiver_viewed=False)
        db.session.add(trade)
        db.session.flush()

        db.session.add(TradeCard(trade_id=trade.id, user_card_id=sender_card.id))
        db.session.add(TradeCard(trade_id=trade.id, user_card_id=receiver_card.id))
        db.session.commit()

        return trade.id


def test_market_trade_button_opens_new_trade(driver):
    username1, email1, password1 = register_user(driver)
    logout_user(driver)
    username2, email2, password2 = register_user(driver)

    other_user_card_id, other_card_id = give_user_card_to_user(username2, "Tailwind", tradable=True, locked=False, uses_remaining=7)
    logout_user(driver)
    login_user(driver, username1, password1)
    driver.get(f"{BASE_URL}/market/{other_card_id}")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Tailwind')]")))
    trade_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Trade")))
    trade_button.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(),'New Trade')]")))
    assert "New Trade" in driver.page_source
    assert "Target User:" in driver.page_source
    assert "Cards Requested:" in driver.page_source


def test_receiver_can_accept_trade_from_trading_page(driver):
    sender_username, sender_email, sender_password = register_user(driver)
    logout_user(driver)

    receiver_username, receiver_email, receiver_password = register_user(driver)

    give_user_card_to_user(sender_username, "Dagger", tradable=True, locked=False, uses_remaining=3)
    give_user_card_to_user(receiver_username, "Tailwind", tradable=True, locked=False, uses_remaining=7)
    create_trade_between_users(sender_username, receiver_username)

    logout_user(driver)
    login_user(driver, receiver_username, receiver_password)

    driver.get(f"{BASE_URL}/trading")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Incoming Trades')]"))
    )

    view_trade_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "View Trade"))
    )
    view_trade_button.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Trade Details')]"))
    )

    accept_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(normalize-space(),'Accept')]"))
    )

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", accept_button)
    driver.execute_script("window.scrollBy(0, 150);")

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(),'Accept')]"))
        )
        accept_button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", accept_button)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Trading')]"))
    )

    assert "Trading" in driver.page_source
