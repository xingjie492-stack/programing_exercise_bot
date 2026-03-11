import pytest
from presentation.views_problem import generate_prompt, generate_problem
from app import app
from models import db, Submissions
from flask_login import login_user
from datetime import datetime
from flask import session

def test_generate_prompt_easy_python():
    prompt = generate_prompt("easy", "python")
    assert "「Python 3 エンジニア認定基礎試験」" in prompt
    assert "python" in prompt

def test_generate_prompt_valueerror():
    with pytest.raises(ValueError):
        generate_prompt("supereasy", "cobol")

@pytest.fixture
def client():
    app_init = app
    app_init.config['TESTING'] = True
    app_init.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app_init.config['WTF_CSRF_ENABLED'] = False
    
    with app_init.test_client() as client:
        with app_init.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_generate_problem_success(logged_in_client, db, monkeypatch):
    # すでにログイン済み、DB初期化済みの logged_in_client が渡される
    response = logged_in_client.post('/problem/generate', data={
        'selected_difficulty': 'easy',
        'selected_language': 'python'
    })
    
    assert response.status_code == 302 # リダイレクトされるはず
    assert "/problem/upload/" in response.location

def test_next_problem(logged_in_client, db, monkeypatch):
    old_sub = Submissions(
        user_id=1,
        problem_text="old_problem_text",
        difficulty="easy",
        language="python",
        create_date=datetime.now()
    )
    db.session.add(old_sub)
    db.session.commit()
    
    monkeypatch.setenv("MOCK_AI", "true")
    
    response = logged_in_client.get(
        f'/problem/generate/{old_sub.submission_id}',
        follow_redirects=True
    )

    assert response.status_code == 200

    all_subs = Submissions.query.all()
    assert len(all_subs) == 2

    new_sub = Submissions.query.order_by(Submissions.submission_id.desc()).first()

    assert new_sub.difficulty == "easy"
    assert new_sub.language == "python"
    assert new_sub.submission_id != old_sub.submission_id
    assert "渡された問題プロンプト" in new_sub.problem_text

def test_show_upload(logged_in_client, db):
    sub = Submissions(
        user_id=1,
        problem_text="problem_text",
        difficulty="easy",
        language="python",
        create_date=datetime.now()
    )
    db.session.add(sub)
    db.session.commit()
    
    response = logged_in_client.get(f'/problem/upload/1/{sub.submission_id}')

    assert response.status_code == 200
    assert b"problem_text" in response.data
    
    with logged_in_client.session_transaction() as sess:
        assert sess['current_problem'] == "problem_text"

def test_show_upload_unauthorized(logged_in_client, db):
    other_sub = Submissions(
        user_id=99,
        problem_text="others_problem_text",
        difficulty="easy",
        language="python",
        create_date=datetime.now()
    )
    db.session.add(other_sub)
    db.session.commit()

    response = logged_in_client.get(f'/problem/upload/1/{other_sub.submission_id}', follow_redirects=True)

    assert "アクセス権限がありません" in response.get_data(as_text=True)
    assert response.request.path == "/presentation/presentation"