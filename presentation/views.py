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

@presentation_bp.route("/presentation")
@login_required
def presentation():
    return render_template("presentation/presentation.html")