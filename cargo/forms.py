from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from cargo.models import User
from cargo.steamapi import SteamAPI
from flask_login import current_user


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=2, max=30)])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Use Login Instead')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterTeamForm(FlaskForm):
    name = StringField('Team Name', validators=[Length(min=2, max=30)])
    player1 = StringField('Player 1 Nickname', validators=[Length(min=2, max=20)])
    player2 = StringField('Player 2 Nickname', validators=[Length(min=2, max=20)])
    player3 = StringField('Player 3 Nickname', validators=[Length(min=2, max=20)])
    player4 = StringField('Player 4 Nickname', validators=[Length(min=2, max=20)])
    player5 = StringField('Player 5 Nickname', validators=[Length(min=2, max=20)])
    player1_steam = StringField('Player 1 Steam Profile URL', validators=[DataRequired()])
    player2_steam = StringField('Player 2 Steam Profile URL', validators=[DataRequired()])
    player3_steam = StringField('Player 3 Steam Profile URL', validators=[DataRequired()])
    player4_steam = StringField('Player 4 Steam Profile URL', validators=[DataRequired()])
    player5_steam = StringField('Player 5 Steam Profile URL', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_player1_steam(self, player1_steam):
        steam_api = SteamAPI()
        steam_id = steam_api.steam_id_profile(player1_steam.data)
        if steam_id:
            pass
        else:
            raise ValidationError('Incorrect steam profile URL')

    def validate_player2_steam(self, player2_steam):
        steam_api = SteamAPI()
        steam_id = steam_api.steam_id_profile(player2_steam.data)
        if steam_id:
            pass
        else:
            raise ValidationError('Incorrect steam profile URL')

    def validate_player3_steam(self, player3_steam):
        steam_api = SteamAPI()
        steam_id = steam_api.steam_id_profile(player3_steam.data)
        if steam_id:
            pass
        else:
            raise ValidationError('Incorrect steam profile URL')

    def validate_player4_steam(self, player4_steam):
        steam_api = SteamAPI()
        steam_id = steam_api.steam_id_profile(player4_steam.data)
        if steam_id:
            pass
        else:
            raise ValidationError('Incorrect steam profile URL')

    def validate_player5_steam(self, player5_steam):
        steam_api = SteamAPI()
        steam_id = steam_api.steam_id_profile(player5_steam.data)
        if steam_id:
            pass
        else:
            raise ValidationError('Incorrect steam profile URL')


class ChangePassword(FlaskForm):
    email = StringField('Email', validators=[Length(min=2, max=20)])
    password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Change')

    def validate_email(self, email):
        other_user = User.query.filter_by(email=email.data).first()
        if other_user:
            if other_user.id != current_user.id:
                raise ValidationError('Email already used! Choose another one')


class CreateTournament(FlaskForm):
    name = StringField('Name of Tournament', validators=[Length(min=2, max=50)])
    type = SelectField('Tournament Type', default='se',
                       choices=[('se', 'Single Elimination'), ('de', 'Double Elimination'), ('rr', 'Round Robin')])
    prize = StringField('Prize Pool', validators=[DataRequired()])
    max_teams = IntegerField('Maximum Teams', validators=[NumberRange(min=2, max=256), DataRequired()])
    third = BooleanField('3rd/4th Decider')
    reg_start = DateField('Reg Start')
    reg_end = DateField('Reg Close')
    tour_start = DateField('Tour Start')
    tour_end = DateField('Tour End')
    paid = BooleanField('Paid Tournament?')
    payment_info = StringField('Payment info for participants (optional)')
    submit = SubmitField('Create Tournament', validators=[DataRequired()])
