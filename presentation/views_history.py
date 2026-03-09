from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Submissions
from flask_login import login_required, current_user
from forms import UsersAnswer
from datetime import datetime
from presentation.views import generate_content

history_bp = Blueprint(
    'history',
    __name__,
    url_prefix='/history'
)

@history_bp.route("/history")
@login_required
def show_history():
    problem_history = Submissions.query.filter_by(user_id=current_user.user_id).all()
    return render_template('presentation/history.html', problem_history=problem_history)

@history_bp.route("/delete/<int:user_id>/<int:submission_id>", methods=["POST"])
@login_required
def delete_history(submission_id, user_id):
    submission = Submissions.query.get_or_404(submission_id)
    if submission.user_id != current_user.user_id:
        flash("削除権限がありません")
        return redirect(url_for("history.show_history"))
    try:
        db.session.delete(submission)
        db.session.commit()
        flash("削除しました。")
        return redirect(url_for("history.show_history"))

    except Exception as e:
        db.session.rollback()
        flash("削除処理中にエラーが発生しました。")
        return redirect(url_for("history.show_history"))

    return redirect(url_for("history.show_history"))

@history_bp.route("delete_all/<int:user_id>", methods=["POST"])
@login_required
def delete_all_history(user_id):
    submissions = Submissions.query.filter_by(user_id = current_user.user_id).all()
    submission = Submissions.query.filter_by(user_id = current_user.user_id).first()
    
    if  not submissions:
        flash ("削除するデータがありません")
        redirect(url_for("history.show_history"))
        return redirect(url_for("history.show_history"))

    if submission.user_id != current_user.user_id:
        flash("権限ないよ")
        redirect(url_for("history.show_history"))

    try:
        for submission in submissions:
            db.session.delete(submission)
        db.session.commit()
        flash("すべての履歴を削除しました")

    except Exception as e:
        db.session.rollback()
        flash("削除処理中にエラーが発生しました")

    return redirect(url_for("history.show_history"))
