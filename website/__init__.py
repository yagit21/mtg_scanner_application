from flask import Flask
from flask_login import LoginManager
from .models import db, User
from .routes import views
from .auth import auth
from .collections import collections

def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = ("hjdfifjsk")
    app.config["SQLALCHEMY_DATABASE_URI"] = ("sqlite:///MTG_Scanner.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(collections)

    login_manager = LoginManager()

    login_manager.login_view = "auth.login_page"

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(
            int(user_id)
        )

    with app.app_context():

        db.create_all()

    return app