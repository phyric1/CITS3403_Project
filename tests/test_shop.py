from app import db
from app.models import User,UserCard,DailyShopCard,Card
from datetime import date

def test_shop_requires_login(client):
    response=client.get("/shop")
    assert response.status_code==302
    assert "/login" in response.headers["Location"]

def test_shop_page_loads(client,user,login):
    login()
    response=client.get("/shop")
    assert response.status_code==200
    assert b"Daily Shop" in response.data

def test_open_easy_pack_without_token(client,user,login):
    login()
    response=client.post("/shop/open_pack/easy", follow_redirects=True)
    assert response.status_code==200
    page_text=response.get_data(as_text=True).lower()
    assert "easy" in page_text
    assert "token" in page_text

def test_open_easy_pack_then_decrease_token(client,app,user,login):
    with app.app_context():
        test=db.session.get(User,user)
        test.easy_tokens=1
        db.session.commit()
    login()
    response=client.post("/shop/open_pack/easy", follow_redirects=True)
    assert response.status_code==200
    with app.app_context():
        test=db.session.get(User,user)
        assert test.easy_tokens==0
