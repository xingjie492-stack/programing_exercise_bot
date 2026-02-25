from flask_wtf import FlaskForm
from models import User, Submissions
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms import (StringField, PasswordField, BooleanField, SubmitField)
from wtforms.validators import DataRequired, Email, Length, Optional

# ログインフォーム
class LoginForm(FlaskForm):
    user_name = StringField(
        "ユーザ名",
        validators=[
            DataRequired('ユーザ名が入力されていません'), 
            Length(max=20, message='20文字以内で入力してください')
            ]
    )
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired('パスワードが入力されていません'), 
            Length(min=4)
            ]
    )
    submit = SubmitField("認証")

# ユーザ登録フォーム
class UserForm(FlaskForm):
    user_name = StringField(
        "ユーザ名",
        validators=[
            DataRequired('ユーザ名は必須です'), 
            Length(max=20, message='20文字以内で入力してください')
            ]
    )
    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired('メールアドレスは必須です'),
            Email()
            ]
    )
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired('パスワードが入力されていません'), 
            Length(4, 10, 'パスワードの長さは4文字以上10文字以内です')
            ]
    )
    is_admin = BooleanField("管理者権限")
    submit = SubmitField("登録")

    # カスタムバリデータ
    def validate_user_name(self, user_name):
        # StringFieldオブジェクトではなく、その中のデータ（文字列をクエリに渡す必要があるため
        # 以下のようにuser_name.dataを使用して、StringFieldから実際の文字列データを取得する
        user = User.query.filter_by(user_name=user_name.data).first()
        if user:
            raise ValidationError(f"ユーザ名'{user_name.data}'は既に存在します。別のユーザ名を入力してください。")

    # カスタムバリデータ
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(f"メールアドレス'{email.data}'は既に存在します。別のメールアドレスを入力してください。")


# ユーザ情報変更フォーム
class UserEditForm(FlaskForm):
    user_name = StringField(
        "ユーザ名",
        validators=[
            DataRequired('ユーザ名は必須です'), 
            Length(max=20, message='20文字以内で入力してください'),
            ]
    )
    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired('メールアドレスは必須です'),
            Email(),
            Optional()
            ]
    )
    password = PasswordField(
        "パスワード(変更しない場合は空欄)",
        validators=[
            Length(4, 10, 'パスワードの長さは4文字以上10文字以内です'),
            ]
    )
    is_admin = BooleanField("管理者権限")
    submit = SubmitField("更新")
    
# カスタムバリデータ
    def validate_user_name(self, user_name):
        user = User.query.filter_by(user_name=user_name.data).first()
        if user:
            raise ValidationError(f"ユーザ名'{user_name.data}'は既に存在します。別のユーザ名を入力してください。")
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(f"メールアドレス'{email.data}'は既に存在します。別のメールアドレスを入力してください。")

    def __init__(self, user_id=None, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.user_id = user_id  # 現在編集中のユーザーIDを保持

    def validate_user_name(self, user_name):
        # 「自分以外」で同じユーザー名を持つ人がいるかチェック
        user = User.query.filter(
            User.user_name == user_name.data,
            User.user_id != self.user_id
        ).first()
        if user:
            raise ValidationError(f"ユーザ名'{user_name.data}'は既に存在します。")

    def validate_email(self, email):
        # 「自分以外」で同じメールアドレスを持つ人がいるかチェック
        user = User.query.filter(
            User.email == email.data,
            User.user_id != self.user_id
        ).first()
        if user:
            raise ValidationError(f"メールアドレス'{email.data}'は既に存在します。")

# ユーザ回答提出フォーム
class UsersAnswer(FlaskForm):
    user_code = StringField("回答", DataRequired('回答を入力してください'))
    submit = SubmitField("提出！")