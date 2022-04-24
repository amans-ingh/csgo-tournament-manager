from cargo import db, login_manager
from flask_login import UserMixin
from flask import redirect, url_for, request


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login', next=request.full_path))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    tournament = db.relationship('Tournament', backref='player', lazy=True)
    team = db.relationship('Team', backref='captain', lazy=True)


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    max_teams = db.Column(db.Integer)
    participants = db.Column(db.Integer, default=0)
    prize = db.Column(db.String)
    reg_start = db.Column(db.String)
    reg_start_time = db.Column(db.String)
    reg_end = db.Column(db.String)
    reg_end_time = db.Column(db.String)
    tour_start = db.Column(db.String)
    tour_end = db.Column(db.String)
    type = db.Column(db.String)
    third = db.Column(db.Boolean)
    reg_no = db.Column(db.Integer, default=0)
    reg_open = db.Column(db.Boolean, default=True)
    paid = db.Column(db.Boolean, default=False)
    payment_info = db.Column(db.String)
    rules = db.Column(db.String)
    admin_wh = db.Column(db.String)
    players_wh = db.Column(db.String)
    discord_invite = db.Column(db.String)
    status = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Integer, db.ForeignKey('user.id'))


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    reg_accepted = db.Column(db.Boolean, default=False)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tour = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    round_num = db.Column(db.Integer)
    match_num = db.Column(db.Integer)
    status = db.Column(db.Integer, nullable=False, default=0)
    maps = db.Column(db.Integer, nullable=False, default=127)
    ip = db.Column(db.String)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    turn = db.Column(db.Boolean, default=True)
    winner = db.Column(db.Integer, db.ForeignKey('team.id'))
    forfeit = db.Column(db.Boolean, default=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    team1_score = db.Column(db.Integer, default=0)
    team2_score = db.Column(db.Integer, default=0)
    api_key = db.Column(db.String)
    matchid = db.Column(db.Integer)


class Servers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    busy = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    ip = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(15), nullable=False)
    flag = db.Column(db.String(2), nullable=False, default='FR')
    logo = db.Column(db.String(4), nullable=False, default='nip')
    p1 = db.Column(db.String)
    p2 = db.Column(db.String)
    p3 = db.Column(db.String)
    p4 = db.Column(db.String)
    p5 = db.Column(db.String)
    p6 = db.Column(db.String)
    p7 = db.Column(db.String)
    p8 = db.Column(db.String)
    p1_steam_id = db.Column(db.String)
    p2_steam_id = db.Column(db.String)
    p3_steam_id = db.Column(db.String)
    p4_steam_id = db.Column(db.String)
    p5_steam_id = db.Column(db.String)
    p6_steam_id = db.Column(db.String)
    p7_steam_id = db.Column(db.String)
    p8_steam_id = db.Column(db.String)


class MapStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    map_number = db.Column(db.Integer)
    map_name = db.Column(db.String(64))
    winner = db.Column(db.Integer, db.ForeignKey('team.id'))
    team1_score = db.Column(db.Integer, default=0)
    team2_score = db.Column(db.Integer, default=0)
    player_stats = db.relationship('PlayerStats', backref='mapstats', lazy='dynamic')

    @staticmethod
    def get_or_create(match_id, map_number, map_name=''):
        match = Match.query.filter_by(matchid=match_id).first()
        if match is None:
            return None

        rv = MapStats.query.filter_by(
            match_id=match_id, map_number=map_number).first()
        if rv is None:
            rv = MapStats()
            rv.match_id = match_id
            rv.map_number = map_number
            rv.map_name = map_name
            rv.team1_score = 0
            rv.team2_score = 0
            db.session.add(rv)
        return rv


class PlayerStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    map_id = db.Column(db.Integer, db.ForeignKey('map_stats.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    steam_id = db.Column(db.String(40))
    name = db.Column(db.String(40))
    kills = db.Column(db.Integer, default=0)
    deaths = db.Column(db.Integer, default=0)
    roundsplayed = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    flashbang_assists = db.Column(db.Integer, default=0)
    teamkills = db.Column(db.Integer, default=0)
    suicides = db.Column(db.Integer, default=0)
    headshot_kills = db.Column(db.Integer, default=0)
    damage = db.Column(db.Integer, default=0)
    bomb_plants = db.Column(db.Integer, default=0)
    bomb_defuses = db.Column(db.Integer, default=0)
    v1 = db.Column(db.Integer, default=0)
    v2 = db.Column(db.Integer, default=0)
    v3 = db.Column(db.Integer, default=0)
    v4 = db.Column(db.Integer, default=0)
    v5 = db.Column(db.Integer, default=0)
    k1 = db.Column(db.Integer, default=0)
    k2 = db.Column(db.Integer, default=0)
    k3 = db.Column(db.Integer, default=0)
    k4 = db.Column(db.Integer, default=0)
    k5 = db.Column(db.Integer, default=0)
    firstkill_t = db.Column(db.Integer, default=0)
    firstkill_ct = db.Column(db.Integer, default=0)
    firstdeath_t = db.Column(db.Integer, default=0)
    firstdeath_ct = db.Column(db.Integer, default=0)

    @staticmethod
    def get_or_create(matchid, mapnumber, steam_id):
        mapstats = MapStats.get_or_create(matchid, mapnumber)

        rv = PlayerStats.query.filter_by(match_id=matchid, steam_id=steam_id, map_id=mapstats.id).first()

        if rv is None:
            rv = PlayerStats()
            rv.match_id = matchid
            rv.map_number = mapstats.id
            rv.steam_id = steam_id
            rv.map_id = mapstats.id
            db.session.add(rv)

        return rv

    def get_rating(self):
        AverageKPR = 0.679
        AverageSPR = 0.317
        AverageRMK = 1.277
        KillRating = float(self.kills) / float(self.roundsplayed) / AverageKPR
        SurvivalRating = float(self.roundsplayed -
                               self.deaths) / self.roundsplayed / AverageSPR
        killcount = float(self.k1 + 4 * self.k2 + 9 *
                          self.k3 + 16 * self.k4 + 25 * self.k5)
        RoundsWithMultipleKillsRating = killcount / \
                                        self.roundsplayed / AverageRMK
        rating = (KillRating + 0.7 * SurvivalRating +
                  RoundsWithMultipleKillsRating) / 2.7
        return rating


class Rounds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer)
    round_num = db.Column(db.String)
    bo = db.Column(db.String)
