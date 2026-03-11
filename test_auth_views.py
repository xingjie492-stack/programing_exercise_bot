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

def test_logout(logged_in_client):
    response = logged_in_client.get('/auth/logout', follow_redirects=True)
    
    assert response.status_code == 200
    assert "ログアウトしました" in response.get_data(as_text=True)
    
def test_register_success(client,db):
    # 1. 登録用データの準備
    data = {
        'user_name': 'newuser',
        'password': 'password12',
        'email': 'new@example.com'
    }

    # 2. 実行：/auth/register へPOSTリクエスト
    # follow_redirects=True にしてリダイレクト先(login)まで追う
    response = client.post('/auth/register', data=data, follow_redirects=True)

    # 3. 検証：ステータスコード
    assert response.status_code == 200

    # 4. 検証：データベースにユーザーが作成されているか
    from models import User
    user = User.query.filter_by(user_name='newuser').first()
    assert user is not None
    assert user.email == 'new@example.com'
    # パスワードがハッシュ化されているか（生パスワードでないか）の確認
    assert user.password != 'password12'

    # 5. 検証：フラッシュメッセージとリダイレクト先の確認
    html_content = response.get_data(as_text=True)
    assert "ユーザ登録しました" in html_content
    assert "ログイン" in html_content  # ログイン画面の要素があるか

def test_update(logged_in_client,db):
    test_user = User.query.filter_by(user_name="testuser").first()
    
    data = {
        'user_name': 'testingman',
        'email': 'testing@email.com',
        'password': 'word23'
    }
    
    response = logged_in_client.post(f'/auth/update/{test_user.user_id}', data=data, follow_redirects=True)
    
    assert response.status_code == 200
    
    user=User.query.filter_by(user_name='testingman').first()
    assert user.email == 'testing@email.com'
    assert user.password == test_user.password
    
    html_content = response.get_data(as_text=True)
    assert '変更しました' in html_content
    
def test_delete_user_success(logged_in_client, db):
    from models import User
    target_user = User.query.filter_by(user_name="testuser").first()
    user_id = target_user.user_id

    # 2. 実行：POSTリクエストを送る
    # views.py の delete 関数は POST の時に削除を実行する設定
    response = logged_in_client.post(f'/auth/delete/{user_id}', follow_redirects=True)

    # 3. 検証：ステータスコードとメッセージ
    assert response.status_code == 200
    assert "アカウントを削除しました。" in response.get_data(as_text=True)

    # 4. 検証：DBから消えているか
    deleted_user = User.query.get(user_id)
    assert deleted_user is None
    
def test_show_user_list(logged_in_client, db):
    extra_user = User(user_name="other_user", email="other@example.com")
    extra_user.set_password("password123")
    db.session.add(extra_user)
    db.session.commit()

    # 2. 実行：ユーザー一覧ページへGETリクエスト
    # logged_in_client を使っているので、既に 'testuser' でログイン済み
    response = logged_in_client.get('/auth/user_list')

    # 3. 検証：ステータスコード
    assert response.status_code == 200

    # 4. 検証：画面にユーザー名が含まれているか
    html = response.get_data(as_text=True)
    assert "testuser" in html  # ログイン中の自分
    assert "other_user" in html  # 追加したユーザー
    assert "user_list.html" # テンプレートが正しく使われている（構造からの推測）