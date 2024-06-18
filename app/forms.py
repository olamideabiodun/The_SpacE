from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User

class LOgin(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    Submit = SubmitField('Sign In')

class Register(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()] )
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Verify Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Oops! Username already exists.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Oops! An account already exists with the same email address.')
        