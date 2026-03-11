import pytest
from app import app as flask_app
from models import db as _db
from models import User, Submissions
from datetime import datetime

@pytest.fixture(scope='session')
def app():
    # 1. テスト用の基本設定
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # メモリDBで高速化・汚染防止
        "WTF_CSRF_ENABLED": False,
        "MOCK_AI": "true"
    })
    
    with flask_app.app_context():
        # セッション全体で一度だけテーブル作成（基本）
        _db.create_all()
        yield flask_app
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    # 各テスト開始時にテーブルをクリーンな状態にする
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all() # テストごとに消すことで UNIQUE エラーを防止

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def logged_in_client(client, db):
    """
    これ一つで「ユーザー作成」と「ログイン状態の維持」を完結させる
    """
    # 1. テストユーザー作成
    test_user = User(
        user_id=1, 
        user_name="testuser", 
        email="test@example.com", 
        is_admin=1
    )
    test_user.set_password("pass123")
    db.session.add(test_user)
    db.session.commit()

    # 2. 実際にログイン処理を走らせてセッションを確立する
    client.post('/auth/', data={
        'user_name': 'testuser',
        'password': 'pass123'
    }, follow_redirects=True)

    yield client