from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Submissions
from flask_login import login_required
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

def generate_content(prompt):
    config ={
        "max_output_tokens": 2000, 
        "temperature": 0.7
    }
    try:
        response = model.generate_content(prompt, generation_config=config)
        return response.text
    except Exception as e:
        raise e

@presentation_bp.route("/upload")
@login_required
def generate_problem():
    form = UsersAnswer()

    if request.method =="GET":
        prompt = """あなたはpythonの教師です。python初学者向けの教科書は一通り読んだという生徒に対して、その実力を試せるコーディングのお題を1問、Markdown形式で出題してください。"""
        problem = generate_content(prompt)
        session['current_problem'] = problem
        submission = Submissions(
            create_date = datetime.now,
            problem_text = problem
        )
        db.session.add(submission)
        db.session.commit
    else:
        problem = session.get('current_problem')
        
    return render_template("presentation/upload.html", problem=problem, form=form)

@presentation_bp.route("/review", methods=["POST"])
@login_required
def review_code():
    form = UsersAnswer()
    problem_text = problem_text = session.get('current_problem', '問題が見つかりませんでした。')
    if form.validate_on_submit():
        prompt = f"""
        あなたは親切で的確なPython講師です。
        以下の「出題した問題」に対して、生徒が作成した「提出コード」を添削し、フィードバックを行ってください。

        ### 1. 出題した問題
        {problem_text}

        ### 2. 生徒の提出コード
        ```python
        {form}
        """

        review = generate_content(prompt)
        # この辺にsubmissionインスタンスにuser_codeとreviewを追加して更新する記述書く
        return render_template("presentation/review.html", review=review)
    flash("バリデーションエラーが発生しました")
    return(url_for("presentation.generate_problem"))

@presentation_bp.route("/presentation")
@login_required
def presentation():
    return render_template("presentation/presentation.html")