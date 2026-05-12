from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, Email


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(), Length(min=3, max=20),
        Regexp(
            r"^[A-Za-z0-9_]+$",
            message="Username can only contain letters, numbers, and underscores"
        )
    ])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
        DataRequired(), Length(min=8, max=128),
        Regexp(
            r'^(?=.*[A-Za-z])(?=.*\d).+$',
            message="Password must contain letters and numbers"
        )
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
                DataRequired(),
                EqualTo("password", message="Passwords must match")
            ])
    submit = SubmitField("Register")

class ResetPasswordForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    email=StringField("Register Email",validators=[DataRequired(),Email()])
    new_password=PasswordField("Password", validators=[
        DataRequired(), Length(min=8, max=128),
        Regexp(
            r'^(?=.*[A-Za-z])(?=.*\d).+$',
            message="Password must contain letters and numbers"
        )
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
                DataRequired(),
                EqualTo("password", message="Passwords must match")
            ])
    submit = SubmitField("Reset Password")