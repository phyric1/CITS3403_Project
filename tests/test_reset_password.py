def test_reset_password_page_loads(client):
    response=client.get("/reset-password")
    assert response.status_code==200
    assert b"Reset Password" in response.data

def test_user_can_reset_password(client,user,login):
    response=client.post("/reset-password",data={
        "username":"test",
        "email":"test@test.com",
        "new_password":"newtest1234",
        "confirm_password":"newtest1234"
    }, follow_redirects=True)
    assert response.status_code==200
    response=login(password="newtest1234")
    assert response.status_code==200
    assert b"test" in response.data

def test_whether_old_password_work(client,user,login):
    response=client.post("/reset-password",data={
        "username":"test",
        "email":"test@test.com",
        "new_password":"newtest1234",
        "confirm_password":"newtest1234"
    }, follow_redirects=True)
    assert response.status_code==200
    response=login(password="test1234")
    assert response.status_code==200
    assert b"Invalid username or password" in response.data

def test_reset_password_with_wrong_email(client,user,login):
    response=client.post("/reset-password",data={
        "username":"test",
        "email":"testtest@test.com",
        "new_password":"newtest1234",
        "confirm_password":"newtest1234"
    }, follow_redirects=True)
    assert response.status_code==200
    assert b"Invalid username or email" in response.data
    response=login(password="test1234")
    assert response.status_code==200
    assert b"test" in response.data

