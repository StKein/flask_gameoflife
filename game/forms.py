from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from game.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class NewGameForm(FlaskForm):
    generations_per_round = IntegerField('Number of generations per round')
    rounds_number = IntegerField('Number of rounds')
    new_cells_per_round = IntegerField('Number of cells to add on each round')
    submit = SubmitField('Start')