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

def login_user(driver,username,password):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.NAME,"username").send_keys(username)
    driver.find_element(By.NAME,"password").send_keys(password)
    click_submit(driver)
    WebDriverWait(driver,10).until(EC.url_contains("/profile/"))

def test_login_page_loads(driver):
    driver.get(f"{BASE_URL}/login")
    assert "Login" in driver.page_source or "Log In" in driver.page_source

def test_register_page_loads(driver):
    driver.get(f"{BASE_URL}/register")
    assert "Register" in driver.page_source

def test_user_can_register(driver):
    username,email,password=register_user(driver)
    assert "/profile/" in driver.current_url
    assert username in driver.page_source

def test_user_can_login_after_register(driver):
    username,email,password=register_user(driver)
    driver.get(f"{BASE_URL}/logout")
    login_user(driver,username,password)
    assert "/profile/" in driver.current_url
    assert username in driver.page_source

def test_wrong_login(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.NAME,"username").send_keys("wrong")
    driver.find_element(By.NAME,"password").send_keys("a1234567")
    click_submit(driver)
    assert "Invalid username or password." in driver.page_source
