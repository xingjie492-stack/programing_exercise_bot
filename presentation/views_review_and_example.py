from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Submissions
from flask_login import login_required, current_user
from forms import UsersAnswer
from datetime import datetime
from presentation.views import generate_content

review_and_example_bp = Blueprint(
    'review_and_example',
    __name__,
    url_prefix='/review_and_example'
)

@review_and_example_bp.route("/review/<int:user_id>/<int:submission_id>", methods=["POST"])
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
            return redirect(url_for("problem.generate_problem"))

        return render_template("presentation/review.html", review=review, submission=submission)
    flash("バリデーションエラーが発生しました")
    return(url_for("problem.generate_problem"))

@review_and_example_bp.route("/reproduce/<int:submission_id>", methods=["POST"])
@login_required
def reproduce_problem(submission_id):
    # 1. 元の問題データを取得
    old_submission = Submissions.query.get_or_404(submission_id)
    
    # 2. 同じ問題内容で新しいレコードを作成 (user_codeやreviewは空のまま)
    new_submission = Submissions(
        user_id = current_user.user_id,
        create_date = datetime.now(),
        problem_text = old_submission.problem_text,
        language = old_submission.language,
        difficulty = old_submission.difficulty# 内容をコピー
    )
    
    db.session.add(new_submission)
    db.session.commit() # 新しいIDが発行される

    # 3. 新しいIDのアップロード画面へリダイレクト
    return redirect(url_for(
        'problem.show_upload', 
        user_id=current_user.user_id, 
        submission_id=new_submission.submission_id
    ))
    
@review_and_example_bp.route("/example/<int:user_id>/<int:submission_id>")
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
