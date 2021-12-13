class Config:
    UPLOAD_FOLDER = 'static/assignments/'
    DATABASE_FOLDER = 'static/database/'
    PLAG_REPORT = 'static/plag_reports/'
    nltk_data = 'static/nltk_data'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_USERNAME = 'example@gmail.com'
    MAIL_PASSWORD = 'password'
    SECRET_KEY = 'idontgiveashit'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
