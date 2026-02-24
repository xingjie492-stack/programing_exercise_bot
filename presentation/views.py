from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Submissions
from flask_login import login_required
import os
from dotenv import load_dotenv
import google.generativeai as genai

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
        "temperature": 0
    }
    try:
        response = model.generate_content(prompt, generation_config=config)
        return response.text
    except Exception as e:
        raise e

@presentation_bp.route("/presentation")
@login_required
def presentation():
    return render_template("presentation/presentation.html")