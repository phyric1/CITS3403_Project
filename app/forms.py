from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[
        DataRequired(), Length(min=6),
        Regexp(
            r'^(?=.*[A-Za-z])(?=.*\d)',
            message="Password must contain letters and numbers"
        )
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
                DataRequired(),
                EqualTo("password", message="Passwords must match")
            ])
    submit = SubmitField("Register")
