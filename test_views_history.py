from models import Submissions, User
from datetime import datetime
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError

def test_delete_all_history_safety(logged_in_client, db):
    test_user = User.query.filter_by(user_name="testuser").first()
    
    # 自分の履歴（複数）
    sub1 = Submissions(user_id=1, problem_text="My Prob 1", create_date=datetime.now())
    sub2 = Submissions(user_id=1, problem_text="My Prob 2", create_date=datetime.now())
    
    # 他人の履歴
    other_sub = Submissions(user_id=99, problem_text="Other User Prob", create_date=datetime.now())
    
    db.session.add_all([sub1, sub2, other_sub])
    db.session.commit()
    
    response = logged_in_client.post(f'history/delete_all/{test_user.user_id}', follow_redirects=True)

    assert  response.status_code == 200

    my_remaining = Submissions.query.filter_by(user_id=1).all()
    assert len(my_remaining) == 0

    others_remaining = Submissions.query.filter_by(user_id=99).all()
    assert len(others_remaining) == 1
    assert others_remaining[0].problem_text == "Other User Prob"

    assert "すべての履歴を削除しました" in response.get_data(as_text=True)
    
def test_delete_history(logged_in_client,db):
    test_user = User.query.filter_by(user_name="testuser").first()
    sub = Submissions(
    user_id=1,
    problem_text="problem_text",
    difficulty="easy",
    language="python",
    create_date=datetime.now()
    )
    db.session.add(sub)
    db.session.commit()

    response = logged_in_client.post(f"/history/delete/{test_user.user_id}/{sub.submission_id}", follow_redirects=True)
    
    assert response.status_code == 200
    my_remaining = Submissions.query.filter_by(user_id=1).all()
    assert len(my_remaining) == 0
    assert "削除しました。" in response.get_data(as_text=True)

def test_delete_history_unauth(logged_in_client, db):
    sub = Submissions(
    user_id=99,
    problem_text="problem_text",
    difficulty="easy",
    language="python",
    create_date=datetime.now()
    )
    db.session.add(sub)
    db.session.commit()
    response = logged_in_client.post(f"/history/delete/1/{sub.submission_id}", follow_redirects=True)
    
    assert response.status_code == 200
    my_remaining = Submissions.query.filter_by(user_id=99).all()
    assert len(my_remaining) == 1
    assert "削除権限がありません" in response.get_data(as_text=True)

def test_delete_history_db_error(logged_in_client , db):
    test_user = User.query.filter_by(user_name="testuser").first()
    # 1. 準備：自分のデータを作成
    sub = Submissions(
        user_id=1,
        problem_text="エラーテスト用",
        language="python",
        difficulty="easy",
        create_date=datetime.now()
    )
    db.session.add(sub)
    db.session.commit()

    # 2. commitメソッドを一時的に「エラーを投げる関数」に差し替える
    original_commit = db.session.commit
    db.session.commit = MagicMock(side_effect=SQLAlchemyError("DB Error"))

    try:
        # 3. 実行：POSTリクエストを送る
        response = logged_in_client.post(
            f'/history/delete/{test_user.user_id}/{sub.submission_id}', 
            follow_redirects=True
        )

        # 4. 検証
        assert response.status_code == 200
        # flashメッセージの確認
        assert "削除処理中にエラーが発生しました。" in response.get_data(as_text=True)
        # ロールバックされてデータが残っているか
        assert Submissions.query.get(sub.submission_id) is not None

    finally:
        # 5. 後片付け：差し替えたcommitを元に戻す（重要！）
        db.session.commit = original_commit