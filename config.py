import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['olamidesokunbi15@gmail.com']
    MAIL_SUBJECT_PREFIX = '[The_SpacE] '
    POSTS_PER_PAGE = 25  # You can adjust this number based on your needs
    
    # Fix PostgreSQL URL if needed (only when DATABASE_URL is set)
    if os.environ.get('postgresql://The_Space_owner:2ziWV0meOKts@ep-restless-smoke-a8eov9ur.eastus2.azure.neon.tech/The_Space?sslmode=require') and os.environ.get('postgresql://The_Space_owner:2ziWV0meOKts@ep-restless-smoke-a8eov9ur.eastus2.azure.neon.tech/The_Space?sslmode=require').startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
        