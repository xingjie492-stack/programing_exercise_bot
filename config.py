# 設定
class Config(object):
    # デバッグモード
    DEBUG = True
    # CSRFやセッションで使用
    SECRET_KEY = "secret-key"
    # 警告対策
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # DB設定
    SQLALCHEMY_DATABASE_URI = "sqlite:///programing_exercise_bot_tables.sqlite"