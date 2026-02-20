from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Submissions
from flask_login import login_required

presentation_bp = Blueprint(
    'presentation', 
    __name__, 
    url_prefix='/presentation'
    )