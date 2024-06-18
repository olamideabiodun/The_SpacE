import os
basedir = os.path.abspath(os.path.dirname(__file__))

class configur:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Lets try this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')

