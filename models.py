from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from sqlalchemy import MetaData

# 命名規則の定義
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# metadataに規則を渡してSQLAlchemyを初期化
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

# ユーザ情報クラス
class User(db.Model, UserMixin):
    __tablename__ = "account" # テーブル名
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # ID(PK)
    user_name = db.Column(db.String(30), unique=True, nullable=False) # ユーザ名
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False) # パスワード
    is_admin = db.Column(db.Boolean, default=True, nullable=False) # 管理者権限の有無
    sign_up_date = db.Column(db.DateTime, server_default=db.func.now()) # 登録日
    
    def get_id(self):
        return self.user_id

    # パスワードをハッシュ化して設定する
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # 入力したパスワードとハッシュ化されたパスワードの比較
    def check_password(self, password):
        return check_password_hash(self.password, password)


# 問題履歴クラス
class Submissions(db.Model):
    __tablename__ = "submissions" # テーブル名
    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # ID(PK)
    user_id = db.Column(db.Integer, db.ForeignKey('account.user_id'), nullable=False) # ユーザID(FK)
    create_date = db.Column(db.DateTime, server_default=db.func.now()) # 作成日
    problem_text = db.Column(db.Text, nullable=False) # 問題文
    user_code = db.Column(db.Text, nullable=False) # ユーザ回答
    review = db.Column(db.Text) # レビュー
    reference_solution = db.Column(db.Text) # 参考解答
    difficulty = db.Column(db.String(20)) # 難易度
    language = db.Column(db.String(20)) # 言語