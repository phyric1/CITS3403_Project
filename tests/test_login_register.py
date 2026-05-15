def test_login_page_loads(client):
    response=client.get("/login")
    assert response.status_code==200
    assert b"Login" in response.data

def test_register_page_loads(client):
    response=client.get("/register")
    assert response.status_code==200
    assert b"Register" in response.data

def test_user_can_register(client):
    response=client.post("/register",data={
        "username":"newuser",
        "email":"newuser@test.com",
        "password":"newuser1234",
        "confirm_password":"newuser1234"
    }, follow_redirects=True)
    assert response.status_code==200
    assert b"newuser" in response.data

def test_register_with_same_username(client, user):
    response=client.post("/register",data={
        "username":"test",
        "email":"testtest@test.com",
        "password":"test1234",
        "confirm_password":"test1234"
    }, follow_redirects=True)
    assert response.status_code==200
    assert b"Username is already taken." in response.data

def test_register_with_same_email(client, user):
    response=client.post("/register",data={
        "username":"new",
        "email":"test@test.com",
        "password":"test1234",
        "confirm_password":"test1234"
    }, follow_redirects=True)
    assert response.status_code==200
    assert b"Email is already registered." in response.data

def test_user_can_login(client,user,login):
    response=login()
    assert response.status_code==200
    assert b"test" in response.data

def test_user_login_with_wrong_password(client,user,login):
    response=login(password="wrong1234")
    assert response.status_code==200
    assert b"Invalid username or password" in response.data

def test_user_can_logout(client,user,login):
    login()
    response=client.get("/logout", follow_redirects=True)
    assert response.status_code==200
    assert b"Login" in response.data or b"Not logged in" in response.data