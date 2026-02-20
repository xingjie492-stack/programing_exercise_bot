from flask import Flask, render_template
from flask_migrate import Migrate
from models import db, User
from flask_login import LoginManager
from auth.views import auth_bp
from presentation.views import presentation_bp

# Flaskアプリケーションのインスタンス生成
app = Flask(__name__)
# 設定ファイル(config.py)読み込み
app.config.from_object("config.Config")
# dbとFlaskの紐づけ
db.init_app(app)
# マイグレーション用オブジェクトの初期化
migrate = Migrate(app, db)
# LoginManagerインスタンス
login_manaagaer = LoginManager()
# Flask-loginの管理オブジェクト生成
login_manaagaer.init_app(app)
# ログインしていないユーザが保護ページにアクセスした際の表示メッセージ
login_manaagaer.login_message = "認証していません：ログインしてください"
# 未認証のユーザがアクセスしようとした際にリダイレクトされる関数を設定
login_manaagaer.login_view = "auth.login"
# blueprintをアプリケーションに登録
app.register_blueprint(auth_bp)
app.register_blueprint(presentation_bp)

# 404エラー時の処理
@app.errorhandler(404)
def not_found(error):
    # errorには例外情報が入ってくる(必要に応じてログ出力なども可能)
        return render_template("errors/404.html", msg="ページが見つかりませんでした(404)"), 404

# セッションのuser_idをベースにUserの詳細情報を取得するための処理
# templateでcurrent_userでユーザ情報にアクセスできるようになる
@login_manaagaer.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 実行
if __name__ == "__main__":
    app.run()