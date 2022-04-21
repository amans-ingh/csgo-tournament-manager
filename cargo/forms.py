import datetime

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from wtforms.widgets import TextArea

from cargo.discordapi import check_discord_webhook
from cargo.models import User
from cargo.steamapi import SteamAPI
from flask_login import current_user


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=2, max=30)])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    recaptcha = RecaptchaField()
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
    player1 = StringField('Player 1 *', validators=[DataRequired()])
    player2 = StringField('Player 2')
    player3 = StringField('Player 3')
    player4 = StringField('Player 4')
    player5 = StringField('Player 5')
    player6 = StringField('Coach (if any)')
    player7 = StringField('Substitute 1 (if any)')
    player8 = StringField('Substitute 2 (if any)')
    player1_steam = StringField('Steam Profile URL *')
    player2_steam = StringField('Steam Profile URL')
    player3_steam = StringField('Steam Profile URL')
    player4_steam = StringField('Steam Profile URL')
    player5_steam = StringField('Steam Profile URL')
    player6_steam = StringField('Steam Profile URL')
    player7_steam = StringField('Steam Profile URL')
    player8_steam = StringField('Steam Profile URL')
    submit = SubmitField('Update')

    def validate_player1_steam(self, hello):
        if self.player1.data:
            if self.player1_steam.data:
                steam_api = SteamAPI()
                steam_id = steam_api.steam_id_profile(self.player1_steam.data)
                if steam_id:
                    self.player1_steam.data = steam_id
                    pass
                else:
                    raise ValidationError('Incorrect Steam profile URL')
            else:
                raise ValidationError('Please input Steam profile URL')
        else:
            pass

    def validate_player2_steam(self, hello):
        if self.player2.data:
            if self.player2_steam.data:
                steam_api = SteamAPI()
                steam_id = steam_api.steam_id_profile(self.player2_steam.data)
                if steam_id:
                    self.player2_steam.data = steam_id
                    pass
                else:
                    raise ValidationError('Incorrect Steam profile URL')
            else:
                raise ValidationError('Please input Steam profile URL')
        else:
            pass

    def validate_player3_steam(self, hello):
        if self.player3.data:
            if self.player3_steam.data:
                steam_api = SteamAPI()
                steam_id = steam_api.steam_id_profile(self.player3_steam.data)
                if steam_id:
                    self.player3_steam.data = steam_id
                    pass
                else:
                    raise ValidationError('Incorrect Steam profile URL')
            else:
                raise ValidationError('Please input Steam profile URL')
        else:
            pass

    def validate_player4_steam(self, hello):
        if self.player4.data:
            if self.player4_steam.data:
                steam_api = SteamAPI()
                steam_id = steam_api.steam_id_profile(self.player4_steam.data)
                if steam_id:
                    self.player4_steam.data = steam_id
                    pass
                else:
                    raise ValidationError('Incorrect Steam profile URL')
            else:
                raise ValidationError('Please input Steam profile URL')
        else:
            pass

    def validate_player5_steam(self, hello):
        if self.player5.data:
            if self.player5_steam.data:
                steam_api = SteamAPI()
                steam_id = steam_api.steam_id_profile(self.player5_steam.data)
                if steam_id:
                    self.player5_steam.data = steam_id
                    pass
                else:
                    raise ValidationError('Incorrect Steam profile URL')
            else:
                raise ValidationError('Please input Steam profile URL')
        else:
            pass

    def validate_player6_steam(self, hello):
        if self.player6.data:
            if self.player6_steam.data:
                steam_api = SteamAPI()
                steam_id = steam_api.steam_id_profile(self.player6_steam.data)
                if steam_id:
                    self.player6_steam.data = steam_id
                    pass
                else:
                    raise ValidationError('Incorrect Steam profile URL')
            else:
                raise ValidationError('Please input Steam profile URL')
        else:
            pass

    def validate_player7_steam(self, hello):
        if self.player7.data:
            if self.player7_steam.data:
                steam_api = SteamAPI()
                steam_id = steam_api.steam_id_profile(self.player7_steam.data)
                if steam_id:
                    self.player7_steam.data = steam_id
                    pass
                else:
                    raise ValidationError('Incorrect Steam profile URL')
            else:
                raise ValidationError('Please input Steam profile URL')
        else:
            pass

    def validate_player8_steam(self, hello):
        if self.player8.data:
            if self.player7_steam.data:
                steam_api = SteamAPI()
                steam_id = steam_api.steam_id_profile(self.player8_steam.data)
                if steam_id:
                    self.player8_steam.data = steam_id
                    pass
                else:
                    raise ValidationError('Incorrect Steam profile URL')
            else:
                raise ValidationError('Please input Steam profile URL')
        else:
            pass


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
    name = StringField('Name of Tournament', validators=[Length(min=2, max=50), DataRequired()])
    type = SelectField('Tournament Type', default='se',
                       choices=[('se', 'Single Elimination'), ('de', 'Double Elimination'), ('rr', 'Round Robin')])
    prize = StringField('Prize Pool', validators=[DataRequired()])
    max_teams = IntegerField('Maximum Teams *', validators=[NumberRange(min=2, max=256), DataRequired()])
    third = BooleanField('3rd/4th Decider')
    reg_start = DateField('Reg Start', validators=[DataRequired()])
    reg_start_time = StringField('Time', validators=[DataRequired()])
    reg_end_time = StringField('Time', validators=[DataRequired()])
    reg_end = DateField('Reg Close', validators=[DataRequired()])
    tour_start = DateField('Tour Start', validators=[DataRequired()])
    tour_end = DateField('Tour End')
    rules = StringField("Rules and Regulations", widget=TextArea())
    admin_wh = StringField("Discord Webhook for Admin notification", validators=[DataRequired()])
    players_wh = StringField("Discord Webhook for participants notification", validators=[DataRequired()])
    discord_invite = StringField("Your Discord Server invite code", validators=[DataRequired()])
    submit = SubmitField('Create Tournament', validators=[DataRequired()])

    def validate_admin_wh(self, admin_wh):
        if not check_discord_webhook(admin_wh.data):
            raise ValidationError("Incorrect Discord Webhook API link")

    def validate_players_wh(self, players_wh):
        if not check_discord_webhook(players_wh.data):
            raise ValidationError("Incorrect Discord Webhook API link")

    def validate_reg_start_time(self, time):
        if ":" not in str(time.data):
            raise ValidationError("Incorrect time format")
        t = str(time.data).replace(' ', '').split(':')
        try:
            hh = int(t[0])
            mm = int(t[1])
        except:
            raise ValidationError("Incorrect time format")
        if not (0<=hh<24 and 0<=mm<=59):
            raise ValidationError("Incorrect time entered")

    def validate_reg_end_time(self, time):
        if ":" not in str(time.data):
            raise ValidationError("Incorrect time format")
        t = str(time.data).replace(' ', '').split(':')
        try:
            hh = int(t[0])
            mm = int(t[1])
        except:
            raise ValidationError("Incorrect time format")
        if not (0<=hh<24 and 0<=mm<=59):
            raise ValidationError("Incorrect time entered")
        yys = str(self.reg_start.data).split("-")[0]
        mms = str(self.reg_start.data).split("-")[1]
        dds = str(self.reg_start.data).split("-")[2]
        hhs = str(self.reg_start_time.data).split(":")[0]
        mins = str(self.reg_start_time.data).split(":")[1]
        yye = str(self.reg_end.data).split("-")[0]
        mme = str(self.reg_end.data).split("-")[1]
        dde = str(self.reg_end.data).split("-")[2]
        date_start = datetime.datetime(int(yys), int(mms), int(dds), int(hhs), int(mins))
        date_end = datetime.datetime(int(yye), int(mme), int(dde), int(hh), int(mm))
        if date_start > date_end:
            raise ValidationError("End Date cannot be before start date")


class AddServerForm(FlaskForm):
    name = StringField('Server Name', validators=[Length(min=2, max=50)])
    ip = StringField('IP address', validators=[Length(min=2, max=50)])
    port = IntegerField('Port', validators=[DataRequired()])
    password = StringField('RCON Password')
    submit = SubmitField('Add Server', validators=[DataRequired()])


class ScheduleMatch(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    time = StringField('Time (HH:MM)(24-Hour)')
    submit = SubmitField('Save')

    def validate_time(self, time):
        if ":" not in str(time.data):
            raise ValidationError("Incorrect time format")
        t = str(time.data).replace(' ', '').split(':')
        try:
            hh = int(t[0])
            mm = int(t[1])
        except:
            raise ValidationError("Incorrect time format")
        if not (0<=hh<24 and 0<=mm<=59):
            raise ValidationError("Incorrect time entered")
