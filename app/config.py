import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'conn-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    # If using Neon, replace 'postgres://' with 'postgresql://' in the URL
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 25
    MAIL_SERVER = os.environ.get('smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('587'))
    MAIL_USE_TLS = os.environ.get('True')
    MAIL_USERNAME = os.environ.get('olamidesokunbi15@gmail.com')
    MAIL_PASSWORD = os.environ.get('Olamide15')
    ADMINS = ['olamidesokunbi15@gmail.com']