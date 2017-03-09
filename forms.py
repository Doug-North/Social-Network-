from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('Use r with that email already exists.')


class RegistrationForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message="Letters, numbers & underscores only"
            ),
            name_exists
        ])

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=5),
            EqualTo('password2', message='Passwords Must Match')
        ]
    )

    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired()])


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])


class PostForm(Form):
    content = TextAreaField('Enter Here...', validators=[DataRequired()])
