from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User
from forms import LoginForm, UserForm
from flask_login import login_user, logout_user, login_required

# authのBlueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')