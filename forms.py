from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, Length, URL, ValidationError, Optional
from models import User
from flask import g, request


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField(
        'Username',
        validators=[DataRequired()],
    )

    email = StringField(
        'E-mail',
        validators=[DataRequired(), Email()],
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)],
    )

    image_url = StringField(
        '(Optional) Image URL',
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[DataRequired()],
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)],
    )


class EditUser(FlaskForm):

    username = StringField(
        'Username',
        validators=[DataRequired()]
    )

    email = StringField(
        'E-mail',
        validators=[Email()],
    )

    image_url = StringField(
        '(Optional) Image URL',
        validators=[URL(), Optional()]
    )

    header_image_url = StringField(
        '(Optional) Header Image URL',
        validators=[URL(), Optional()]
    )

    bio = TextAreaField(
        'Bio',
        validators=[Optional()]
    )

    location = StringField(
        'Location',
        validators=[Optional()]
    )


    password = PasswordField(
        'Confrim password',
        validators=[Length(min=6)],
    )


    """custom validation methods"""
    def validate_password(self, field):
        """authenticates password from edit submission"""

        if not User.authenticate(g.user.username, field.data):
            raise ValidationError('Incorrect password, please try again.')

    def validate_username(self, field):
        """validates that new username is unique in database"""

        existing_user = User.query.filter_by(username=field.data).one_or_none()
        if existing_user and existing_user.username != g.user.username:
            raise ValidationError('Username is already taken.')

    def validate_email(self, field):
        """validates that new email is unique in database"""

        existing_user = User.query.filter_by(email=field.data).one_or_none()
        if existing_user and existing_user.email != g.user.email:
            raise ValidationError('Email is already taken.')


class CSRFForm(FlaskForm):
    """empty form for CSRF protection"""

