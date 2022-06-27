from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email


class CreateCafeForm(FlaskForm):
    name = StringField("Cafe name", validators=[DataRequired()])
    location = StringField("Cafe location (City)", validators=[DataRequired()])
    map_url = StringField("Cafe map URL", validators=[DataRequired(), URL()])
    img_url = StringField("Cafe Image URL", validators=[DataRequired(), URL()])
    has_wifi = StringField("Has wifi ? (Y or N)", validators=[DataRequired()])
    has_sockets = StringField("Has sockets ? (Y or N)", validators=[DataRequired()])
    has_toilet = StringField("Has toilet ? (Y or N)", validators=[DataRequired()])
    can_take_calls = StringField("Can take calls ? (Y or N)", validators=[DataRequired()])
    seats = StringField("How many seats?")
    coffee_price = StringField("Coffee price?")
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
