from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LOgin(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    Submit = SubmitField('Sign In')