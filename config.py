import os
class configur:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Lets try this'
