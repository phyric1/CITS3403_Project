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
    options=Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    browser=webdriver.Chrome(options=options)
    yield browser
    browser.quit()

def make_user():
    suffix=str(int(time.time() * 1000))[-8:]
    username=f"selenium{suffix}"
    email=f"selenium{suffix}@test.com"
    password="test1234"
    return username,email,password

def click_submit(driver):
    driver.find_element(By.CSS_SELECTOR,"input[type='submit'],button[type='submit']").click()

def register_user(driver):
    username,email,password=make_user()
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.NAME,"username").send_keys(username)
    driver.find_element(By.NAME,"email").send_keys(email)
    driver.find_element(By.NAME,"password").send_keys(password)
    driver.find_element(By.NAME,"confirm_password").send_keys(password)
    click_submit(driver)
    WebDriverWait(driver,10).until(EC.url_contains("/profile/"))
    return username,email,password

def give_user_gold(username,amount):
    from app import create_app, db
    from app.models import User
    flask_app=create_app()
    with flask_app.app_context():
        user=User.query.filter_by(username=username).first()
        assert user is not None
        user.gold=amount
        db.session.commit()

def scroll_and_click(driver,element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});",element)
    WebDriverWait(driver,10).until(lambda d: element.is_displayed() and element.is_enabled())
    element.click()

def test_shop_redirects_to_login_if_when_logged_out(driver):
    driver.get(f"{BASE_URL}/shop")
    WebDriverWait(driver,10).until(EC.url_contains("/login"))
    assert "/login" in driver.current_url
    assert "Login" in driver.page_source or "Log In" in driver.page_source

def test_shop_loads_when_login(driver):
    username,email,password=register_user(driver)
    driver.get(f"{BASE_URL}/shop")
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//h1[contains(normalize-space(), 'Daily Shop')]")))
    assert "Daily Shop" in driver.page_source
    assert "Common Pack" in driver.page_source
    assert "/shop" in driver.current_url

def test_open_common_pack_without_token_is_disabled(driver):
    username,email,password=register_user(driver)
    driver.get(f"{BASE_URL}/shop")
    common_pack_button=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//button[contains(normalize-space(),'Open Common Pack')]")))
    assert "/shop" in driver.current_url
    assert not common_pack_button.is_enabled()

def test_inventory_loads_from_profile(driver):
    username,email,password=register_user(driver)
    inventory_link=WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT,"Inventory")))
    inventory_link.click()
    WebDriverWait(driver,10).until(lambda d: "inventory" in d.current_url.lower() or "Inventory" in d.page_source)
    assert "Inventory" in driver.page_source

def test_inventory_shows_start_cards(driver):
    username,email,password=register_user(driver)
    driver.get(f"{BASE_URL}/profile/{username}/inventory")
    WebDriverWait(driver,10).until(lambda d: "Inventory" in d.page_source)
    page_text=driver.page_source
    assert "Inventory" in page_text
    assert (
        "Silence Falls" in page_text
        or "Tailwind" in page_text
        or "Dagger" in page_text
        or "Dexterity" in page_text
        or "Rest" in page_text
    )

def test_buy_card_from_shop_the_button_changes(driver):
    username,email,password=register_user(driver)
    give_user_gold(username,1000)
    driver.get(f"{BASE_URL}/shop")
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//h1[contains(normalize-space(),'Daily Shop')]")))
    buy_button=driver.find_element(By.XPATH,"//button[normalize-space()='Buy']")
    old_page=driver.find_element(By.TAG_NAME,"html")
    buy_button.click()
    WebDriverWait(driver,10).until(EC.staleness_of(old_page))
    WebDriverWait(driver,10).until(lambda d: "Purchased" in d.page_source or "Sold Out" in d.page_source)
    page_text=driver.page_source
    assert "Purchased" in page_text or "Sold Out" in page_text
    assert "/shop" in driver.current_url

def test_inventory_can_add_and_remove_card_from_deck(driver):
    username,email,password=register_user(driver)
    driver.get(f"{BASE_URL}/profile/{username}/inventory?mode=deck")
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"inventory")))
    deck_count=driver.find_element(By.ID,"deck-count")
    start_count=int(deck_count.text)
    add_button=WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#inventory .add-to-deck")))
    scroll_and_click(driver,add_button)
    WebDriverWait(driver,10).until(lambda d: int(d.find_element(By.ID,"deck-count").text) == start_count+1)
    remove_button=WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#deck .remove-from-deck")))
    scroll_and_click(driver,remove_button)
    WebDriverWait(driver,10).until(lambda d: int(d.find_element(By.ID,"deck-count").text) == start_count)
    assert int(driver.find_element(By.ID,"deck-count").text) == start_count

def test_inventory_can_make_card_tradable(driver):
    username,email,password=register_user(driver)
    driver.get(f"{BASE_URL}/profile/{username}/inventory?mode=tradable")
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"inventory")))
    tradable_button=WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#inventory .tradable-toggle[data-tradable='false']")))
    scroll_and_click(driver,tradable_button)
    WebDriverWait(driver,10).until(lambda d: len(d.find_elements(By.CSS_SELECTOR,"#inventory .tradable-toggle[data-tradable='true']")) > 0)
    page_text=driver.page_source
    assert "Tradable" in page_text
