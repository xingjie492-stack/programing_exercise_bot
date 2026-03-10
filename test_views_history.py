from models import Submissions, User
from datetime import datetime

def test_delete_all_history_safety(auth_client, db):
    # 自分の履歴（複数）
    sub1 = Submissions(user_id=1, problem_text="My Prob 1", create_date=datetime.now())
    sub2 = Submissions(user_id=1, problem_text="My Prob 2", create_date=datetime.now())
    
    # 他人の履歴
    other_sub = Submissions(user_id=99, problem_text="Other User Prob", create_date=datetime.now())
    
    db.session.add_all([sub1, sub2, other_sub])
    db.session.commit()
    
    response = auth_client.post('history/delete_all/1', follow_redirects=True)

    assert  response.status_code == 200

    my_remaining = Submissions.query.filter_by(user_id=1).all()
    assert len(my_remaining) == 0

    others_remaining = Submissions.query.filter_by(user_id=99).all()
    assert len(others_remaining) == 1
    assert others_remaining[0].problem_text == "Other User Prob"

    assert "すべての履歴を削除しました" in response.get_data(as_text=True)