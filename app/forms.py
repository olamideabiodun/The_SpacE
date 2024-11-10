from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User
from wtforms import TextAreaField
from wtforms.validators import Length

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


class EditProfile(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=180)])
    submit = SubmitField('Save')

    def __init__(self, originalUsername, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.originalUsername = originalUsername
    
    def validate_username(self, username):
        if username.data != self.originalUsername:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data
            ))
            if user is not None:
                raise ValidationError('Please use different username!')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), 
        Length(min=1, max=140)
    ])
    submit = SubmitField('Post')