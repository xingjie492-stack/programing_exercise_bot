from models import User
from flask import url_for

def test_login_success(logged_in_client, db):
    # 1. 重複防止：既存の同名ユーザーを削除
    existing_user = User.query.filter_by(user_name="testuser").first()
    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()

    # 2. あらためてテスト用ユーザーを作成
    test_user = User(user_name="testuser", email="test@example.com", is_admin=1)
    test_user.set_password("password123")
    db.session.add(test_user)
    db.session.commit()

    # 3. ログイン実行
    response = logged_in_client.post('/auth/', data={
        'user_name': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "認証不備" not in response.get_data(as_text=True)
    
def test_login_failure(logged_in_client, db):
    # 1. 重複防止：既存の同名ユーザーを削除
    existing_user = User.query.filter_by(user_name="testuser").first()
    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()

    # 2. あらためてテスト用ユーザーを作成
    test_user = User(user_name="testuser", email="test@example.com", is_admin=1)
    test_user.set_password("password123")
    db.session.add(test_user)
    db.session.commit()

    # 3. ログイン実行
    response = logged_in_client.post('/auth/', data={
        'user_name': 'nottestuser',
        'password': 'notpassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "認証不備" in response.get_data(as_text=True)

# def test_logout(auth_client):
#     response = auth_client.get('/auth/logout', follow_redirects=True)
    
#     assert response.status_code == 200
#     assert "ログアウトしました" in response.get_data(as_text=True)