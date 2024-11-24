from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo
from app.models import User

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)
    ])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfile(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=140)
    ])
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Request Password Reset')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[
        DataRequired(), Length(min=1, max=140)
    ])
    submit = SubmitField('Submit') 