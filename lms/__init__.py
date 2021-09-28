import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

UPLOAD_FOLDER = 'static/assignments'
log_file = 'lms/static/logfile.txt'
nltk_data = 'static/nltk_data'
ALLOWED_EXTENSIONS = {'pdf'}
today = datetime.datetime.now()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'idontgiveashit'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
app.config['MAIL_USERNAME'] = 'example@gmail.com'
app.config['MAIL_PASSWORD'] = 'password'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mail = Mail(app)

from lms import routes
