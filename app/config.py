# import os
# from dotenv import load_dotenv

# basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv()

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY')
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     POSTS_PER_PAGE = 25
#     MAIL_SERVER = os.environ.get('MAIL_SERVER')
#     MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
#     MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
#     MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
#     MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
#     ADMINS = ['olamidesokunbi15@gmail.com']