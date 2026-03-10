import pytest
from app import app as flask_app # app生成関数がある前提
from models import db as _db
from models import User, Submissions # モデルもインポート
from datetime import datetime

@pytest.fixture(scope='session')
def app():
    # テスト用に設定を上書き
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "MOCK_AI": "true"
    })
    
    with flask_app.app_context():
        yield flask_app

@pytest.fixture(scope='function')
def db(app):
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, db):
    """ログイン済みの状態のクライアントを作成する"""
    # 1. テスト用のユーザーを作成
    test_user = User(user_id=1, user_name="testuser", email="tedt@testing.com", password="password", is_admin=True, sign_up_date=datetime.now()) # あなたのUserモデルに合わせて調整
    db.session.add(test_user)
    db.session.commit()

    # 2. flask_login の login_user をシミュレート
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.user_id)
        sess['_fresh'] = True
    
    return client