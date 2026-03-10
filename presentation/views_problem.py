from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Submissions
from flask_login import login_required, current_user
from forms import UsersAnswer
from datetime import datetime
from presentation.views import generate_content

problem_bp = Blueprint(
    'problem',
    __name__,
    url_prefix='/problem'
)

def generate_prompt(difficulty,language):
        def catch_diff_and_lang(d,l):
            return d,l

        difficulty, language = catch_diff_and_lang(difficulty, language)
    
        # 1. AIで問題を生成
        if language == "python":
            if difficulty == "easy":
                prompt = f"""
                あなたはプログラミング言語「{ language }」の講師です。
                これから「Python 3 エンジニア認定基礎試験」に臨む生徒に対して、その実力を試せるコーディング演習問題をMarkdown形式で一問出題してください。
                なお、ここで模範解答は提示しないでください。
                """
            elif difficulty == "normal":
                prompt = f"""
                あなたはプログラミング言語「{ language }」の講師です。
                これから「Python 3 エンジニア認定基礎試験」に臨む生徒に対して、その実力を試せるコーディング演習問題をMarkdown形式で一問出題してください。
                なお、ここで模範解答は提示しないでください。
                """
            elif difficulty =="hard":
                prompt = f"""
                あなたはプログラミング言語「{ language }」の講師です。
                これから「PCPP1」に臨む生徒に対して、その実力を試せるコーディング演習問題をMarkdown形式で一問出題してください。
                なお、ここで模範解答は提示しないでください。
                """
            else:
                raise ValueError(f"無効な難易度設定です")

        elif language == "Java":
            if difficulty == "easy":
                prompt = f"""
                あなたはプログラミング言語「{ language }」の講師です。
                「Oracle Java Bronze」受験に臨む生徒に対して、その実力を試せるコーディング演習問題をMarkdown形式で一問出題してください。
                なお、ここで模範解答は提示しないでください。
                """
            elif difficulty == "normal":
                prompt = f"""
                あなたはプログラミング言語「{ language }」の講師です。
                「Oracle Java Silver」受験に臨む生徒に対して、その実力を試せるコーディング演習問題をMarkdown形式で一問出題してください。
                なお、ここで模範解答は提示しないでください。
                """
            elif difficulty =="hard":
                prompt = f"""
                あなたはプログラミング言語「{ language }」の講師です。
                これから「PCPP1」に臨む生徒に対して、その実力を試せるコーディング演習問題をMarkdown形式で一問出題してください。
                なお、ここで模範解答は提示しないでください。
                """
            else:
                raise ValueError(f"無効な難易度設定です")


        elif language == "C language":
            if difficulty == "easy":
                prompt = f"""
                あなたはプログラミング言語「{ language }」の講師です。
                「C言語プログラミング能力認定試験3級」受験に臨む生徒に対して、その実力を試せるコーディング演習問題をMarkdown形式で一問出題してください。
                なお、ここで模範解答は提示しないでください。
                """
            elif difficulty == "normal":
                prompt = f"""
                あなたはプログラミング言語「{ language }」の講師です。
                「C言語プログラミング能力認定試験2級」受験に臨む生徒に対して、その実力を試せるコーディング演習問題をMarkdown形式で一問出題してください。
                なお、ここで模範解答は提示しないでください。
                """
            elif difficulty =="hard":
                prompt = f"""
                あなたはプログラミング言語「{ language }」の講師です。
                これから「PCPP1」に臨む生徒に対して、その実力を試せるコーディング演習問題をMarkdown形式で一問出題してください。
                なお、ここで模範解答は提示しないでください。
                """
            else:
                raise ValueError(f"無効な難易度設定です")

        else:
            raise ValueError(f"Unsupported language: {language}")
        
        return prompt

@problem_bp.route("/generate", methods=["POST"])
@login_required
def generate_problem():
    selected_diff = request.form.get('selected_difficulty')
    selected_lang = request.form.get('selected_language')
    
    prompt = generate_prompt(selected_diff,selected_lang)

    problem = generate_content(prompt,"problem")
    
    # 2. データベースに下書き（回答前）として保存
    submission = Submissions(
        user_id = current_user.user_id,
        create_date = datetime.now(),
        problem_text = problem,
        difficulty = selected_diff,
        language = selected_lang
    )
    db.session.add(submission)
    db.session.commit() # ここで submission_id が発行される

    # 3. 動的なURL（下記の show_upload 関数）にリダイレクト
    return redirect(url_for(
        'problem.show_upload', 
        user_id=current_user.user_id, 
        submission_id=submission.submission_id
    ))

@problem_bp.route("/generate/<int:submission_id>", methods=["GET"])
@login_required
def next_problem(submission_id):
    old_submission = Submissions.query.get_or_404(submission_id)
    
    # --- デバッグ用プリント ---
    # print(f"DEBUG: diff='{old_submission.difficulty}', lang='{old_submission.language}'")
    
    # prompt = generate_prompt(old_submission.difficulty, old_submission.language)
    
    # # プロンプトが空になっていないかチェック
    # print(f"DEBUG: generated_prompt length={len(prompt) if prompt else 0}")
    # -----------------------

    prompt = generate_prompt(old_submission.difficulty, old_submission.language)
    
    problem = generate_content(prompt, "problem")
    
    # 2. データベースに下書き（回答前）として保存
    submission = Submissions(
        user_id = current_user.user_id,
        create_date = datetime.now(),
        problem_text = problem,
        difficulty = old_submission.difficulty,
        language = old_submission.language
    )
    db.session.add(submission)
    db.session.commit() # ここで submission_id が発行される

    # 3. 動的なURL（下記の show_upload 関数）にリダイレクト
    return redirect(url_for(
        'problem.show_upload', 
        user_id=current_user.user_id, 
        submission_id=submission.submission_id
    ))

@problem_bp.route("/upload/<int:user_id>/<int:submission_id>")
@login_required
def show_upload(user_id, submission_id):
    # URLのIDからDBから問題を特定
    submission = Submissions.query.get_or_404(submission_id)
    
    # 他人の問題が見れないようにチェック
    if submission.user_id != current_user.user_id:
        flash("アクセス権限がありません")
        return redirect(url_for("presentation.presentation"))

    form = UsersAnswer()
    # セッションにも保存（レビュー時に使用するため）
    session['current_problem'] = submission.problem_text
    
    return render_template(
        "presentation/upload.html", 
        problem=submission.problem_text, 
        form=form, 
        submission=submission
    )