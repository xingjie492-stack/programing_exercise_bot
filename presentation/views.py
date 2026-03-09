from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Submissions
from flask_login import login_required, current_user
import os
from dotenv import load_dotenv
import google.generativeai as genai
from forms import UsersAnswer
from datetime import datetime

presentation_bp = Blueprint(
    'presentation', 
    __name__, 
    url_prefix='/presentation'
    )

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def generate_content(prompt,mode):
    if os.getenv("MOCK_AI") == "true":
        
        if mode == "problem":
            return f"渡された問題プロンプト：{ prompt }"
        else:
            return f"渡されたレビュー又は模範解答プロンプト：{ prompt }"
    
    config_problem ={
        "max_output_tokens": 2000, 
        "temperature": 0.7
    }
    
    config_review_and_example = {
        "max_output_tokens": 2000, 
        "temperature": 0
    }
    if mode == "problem":
        try:
            response = model.generate_content(prompt, generation_config=config_problem)
            return response.text
        except Exception as e:
            raise e

    else:
        try:
            response = model.generate_content(prompt, generation_config=config_review_and_example)
            return response.text
        except Exception as e:
            raise e

@presentation_bp.route("/review/<int:user_id>/<int:submission_id>", methods=["POST"])
@login_required
def review_code(user_id, submission_id):
    form = UsersAnswer()
    problem_text = session.get('current_problem', '問題が見つかりませんでした。')
    submission = Submissions.query.get_or_404(submission_id)
    if form.validate_on_submit():
        prompt = f"""
        あなたは親切で的確な{ submission.language }の講師です。
        以下の「出題した問題」に対して、生徒が作成した「提出コード」を100点満点で評価してください。

        ### 1. 出題した問題
        {problem_text}

        ### 2. 生徒の提出コード
        ```python
        {form.user_code.data}
        """

        review = generate_content(prompt,"review")
        # この辺にsubmissionインスタンスにuser_codeとreviewを追加して更新する記述書く
        submission.user_code = form.user_code.data
        submission.review = review

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("データの保存中にエラーが発生しました")
            return redirect(url_for("presentation.generate_problem"))

        return render_template("presentation/review.html", review=review, submission=submission)
    flash("バリデーションエラーが発生しました")
    return(url_for("presentation.generate_problem"))

@presentation_bp.route("/reproduce/<int:submission_id>", methods=["POST"])
@login_required
def reproduce_problem(submission_id):
    # 1. 元の問題データを取得
    old_submission = Submissions.query.get_or_404(submission_id)
    
    # 2. 同じ問題内容で新しいレコードを作成 (user_codeやreviewは空のまま)
    new_submission = Submissions(
        user_id = current_user.user_id,
        create_date = datetime.now(),
        problem_text = old_submission.problem_text # 内容をコピー
    )
    
    db.session.add(new_submission)
    db.session.commit() # 新しいIDが発行される

    # 3. 新しいIDのアップロード画面へリダイレクト
    return redirect(url_for(
        'problem.show_upload', 
        user_id=current_user.user_id, 
        submission_id=new_submission.submission_id
    ))

@presentation_bp.route("/history")
@login_required
def show_history():
    problem_history = Submissions.query.filter_by(user_id=current_user.user_id).all()
    return render_template('presentation/history.html', problem_history=problem_history)

@presentation_bp.route("/example/<int:user_id>/<int:submission_id>")
@login_required
def example_answer(user_id, submission_id):
    problem_text = session.get('current_problem', '問題が見つかりませんでした。')
    submission = Submissions.query.get_or_404(submission_id)
    prompt = f"""
    あなたは親切で的確な{ submission.language }の講師です。
    以下の「出題した問題」に対して、模範解答を一つ示してください。

    ### 1. 出題した問題
    {problem_text}
    """

    example = generate_content(prompt,"example")
    submission.reference_solution = example

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("データの保存中にエラーが発生しました")
        return redirect(url_for("problem.generate_problem"))
    return render_template('presentation/example.html', example=example,submission=submission)

@presentation_bp.route("/delete/<int:user_id>/<int:submission_id>", methods=["POST"])
@login_required
def delete_history(submission_id, user_id):
    submission = Submissions.query.get_or_404(submission_id)
    if submission.user_id != current_user.user_id:
        flash("削除権限がありません")
        return redirect(url_for("presentation.show_history"))
    try:
        db.session.delete(submission)
        db.session.commit()
        flash("削除しました。")
        return redirect(url_for("presentation.show_history"))

    except Exception as e:
        db.session.rollback()
        flash("削除処理中にエラーが発生しました。")
        return redirect(url_for("presentation.show_history"))

    return redirect(url_for("presentation.show_history"))

@presentation_bp.route("delete_all/<int:user_id>", methods=["POST"])
@login_required
def delete_all_history(user_id):
    submissions = Submissions.query.filter_by(user_id = current_user.user_id).all()
    submission = Submissions.query.filter_by(user_id = current_user.user_id).first()
    
    if  not submissions:
        flash ("削除するデータがありません")
        redirect(url_for("presentation.show_history"))
        return redirect(url_for("presentation.show_history"))

    if submission.user_id != current_user.user_id:
        flash("権限ないよ")
        redirect(url_for("presentation.show_history"))

    try:
        for submission in submissions:
            db.session.delete(submission)
        db.session.commit()
        flash("すべての履歴を削除しました")

    except Exception as e:
        db.session.rollback()
        flash("削除処理中にエラーが発生しました")

    return redirect(url_for("presentation.show_history"))

@presentation_bp.route("/presentation")
@login_required
def presentation():
    return render_template("presentation/presentation.html")