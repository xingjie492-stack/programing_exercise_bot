from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User
from forms import LoginForm, UserForm
from flask_login import login_user, logout_user, login_required

# authのBlueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ログイン(Form使用)
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        user = User.query.filter_by(user_name=user_name).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for("product.top"))
        flash("認証不備")
    return render_template("auth/login_form.html", form=form)

# ログアウト
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました")
    return redirect(url_for("auth.login"))

# サインアップ(Form使用)
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = UserForm()
    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        email = form.email.data
        is_admin = form.is_admin.data
        
        user = User(
            user_name=user_name, 
            password=password, 
            email=email, 
            is_admin=is_admin, 
            is_active=True
            )
        
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash("ユーザ登録しました")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register_form.html", form=form)