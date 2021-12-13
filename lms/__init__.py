import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_toastr import Toastr
from lms.Config import Config


ALLOWED_EXTENSIONS = {'pdf'}
logfile = 'lms/static/logfile.txt'
today = datetime.datetime.now().date()
db = SQLAlchemy()
bcrypt = Bcrypt()
toastr = Toastr()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    from lms.main.routes import main
    from lms.users.routes import users
    from lms.courses.routes import courses
    from lms.errors.handler import errors

    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    toastr.init_app(app)
    bcrypt.init_app(app)

    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(courses)
    app.register_blueprint(errors)

    return app


