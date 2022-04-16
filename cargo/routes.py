import json
import os
import time

from flask import render_template, url_for, flash, redirect, request
from cargo import application, bcrypt, db, sock
from cargo.models import User, Team, Tournament, Registration, Servers
from cargo.rcon import GameServer
from cargo.steamapi import SteamAPI
from cargo.forms import RegistrationForm, LoginForm, RegisterTeamForm, ChangePassword, CreateTournament, AddServerForm, \
    ScheduleMatch
from flask_login import login_user, current_user, logout_user, login_required
from cargo.functions import bracket_type, save_tournament, add_team_tournament, delete_team_tournament, load_players, \
    details_from_match_id, veto_status
from cargo.brackets import TournamentBrackets
from secrets import token_hex
import datetime


@application.errorhandler(404)
def page_not_found(e):
    if current_user.is_authenticated:
        return render_template('error.html', error=e, email=current_user.email, title='Page Not Found',
                               user=current_user)
    return render_template('error.html', error=e, title='Page Not found', user=False)


@application.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', email=current_user.email, index=1, user=current_user)
    return render_template('index.html', index=1, user=False)


@application.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get("next")
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(next_url) if next_url else redirect(url_for('index'))
        else:
            flash("Incorrect email or password", "danger")
    return render_template('login.html', title='Login', form=form, user=False)


@application.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.password = hashed_pw
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, user=False)


@application.route('/team', methods=['GET', 'POST'])
@login_required
def team():
    form = RegisterTeamForm()
    my_team = Team.query.filter_by(id=current_user.id).first()
    if form.validate_on_submit():
        steam_api = SteamAPI()
        p1_steam = steam_api.steam_id_profile(form.player1_steam.data)
        p2_steam = steam_api.steam_id_profile(form.player2_steam.data)
        p3_steam = steam_api.steam_id_profile(form.player3_steam.data)
        p4_steam = steam_api.steam_id_profile(form.player4_steam.data)
        p5_steam = steam_api.steam_id_profile(form.player5_steam.data)
        if my_team:
            my_team.name = form.name.data
            my_team.p1 = form.player1.data
            my_team.p1_steam_id = p1_steam
            my_team.p2 = form.player2.data
            my_team.p2_steam_id = p2_steam
            my_team.p3 = form.player3.data
            my_team.p3_steam_id = p3_steam
            my_team.p4 = form.player4.data
            my_team.p4_steam_id = p4_steam
            my_team.p5 = form.player5.data
            my_team.p5_steam_id = p5_steam
        else:
            my_team = Team(user=current_user.id,
                           name=form.name.data,
                           p1=form.player1.data,
                           p1_steam_id=p1_steam,
                           p2=form.player2.data,
                           p2_steam_id=p2_steam,
                           p3=form.player3.data,
                           p3_steam_id=p3_steam,
                           p4=form.player4.data,
                           p4_steam_id=p4_steam,
                           p5=form.player5.data,
                           p5_steam_id=p5_steam)
            db.session.add(my_team)
        db.session.commit()
        flash("Team Information Updated Successfully!", "success")
    elif request.method == 'GET':
        if my_team:
            form.name.data = my_team.name
            form.player1.data = my_team.p1
            form.player2.data = my_team.p2
            form.player3.data = my_team.p3
            form.player4.data = my_team.p4
            form.player5.data = my_team.p5
            form.player1_steam.data = my_team.p1_steam_id
            form.player2_steam.data = my_team.p2_steam_id
            form.player3_steam.data = my_team.p3_steam_id
            form.player4_steam.data = my_team.p4_steam_id
            form.player5_steam.data = my_team.p5_steam_id
    return render_template('team.html', email=current_user.email, form=form, user=current_user, title='Account')


@application.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = ChangePassword()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.password.data):
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.email = form.email.data
            db.session.commit()
            flash('Password changed successfully', 'info')
            return redirect(url_for('index'))
        else:
            flash('Incorrect password!, Please try again.', 'danger')
            return redirect('changepassword')
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('change_password.html', form=form, email=current_user.email, user=current_user,
                           title='Change Password')


@application.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@application.route('/forgot_password')
def forgot_password():
    logout_user()
    return render_template('forgot_password.html', user=False, title='Forgot Password')


@application.route('/organise')
@login_required
def organise_tournament():
    if current_user.is_authenticated:
        tour = Tournament.query.filter_by(admin=current_user.id).all()
        return render_template('organiser.html', page='match_history', user=current_user,
                               title='Organiser Dashboard', tour=tour)
    return redirect(url_for('logout'))


@application.route('/create', methods=['GET', 'POST'])
@login_required
def create_tournament():
    if current_user.is_authenticated:
        form = CreateTournament()
        if form.validate_on_submit():
            tournament = Tournament(name=form.name.data,
                                    type=form.type.data,
                                    prize=form.prize.data,
                                    max_teams=form.max_teams.data,
                                    third=False,
                                    reg_start=str(form.reg_start.data),
                                    reg_end=str(form.reg_end.data),
                                    tour_start=str(form.tour_start.data),
                                    tour_end=str(form.tour_end.data),
                                    admin=current_user.id)
            if form.paid.data:
                tournament.paid = True
                tournament.payment_info = form.payment_info.data
            db.session.add(tournament)
            db.session.commit()
            save = Tournament.query.filter_by(admin=current_user.id).all()
            save_tournament(save[-1])
            tourney_matches = TournamentBrackets(tournament)
            if form.type.data == 'se':
                for i in range(8):
                    tourney_matches.single_elimination(i)
            return redirect(url_for('organise_tournament'))
        return render_template('create_tournament.html', user=current_user, title='Create Tournament', form=form)


@application.route('/organise/<int:id>/dashboard')
@login_required
def tournament(id):
    tour = Tournament.query.filter_by(id=id).first()
    if tour:
        if tour.admin == current_user.id:
            registrations = Registration.query.filter_by(tour_id=tour.id).all()
            servers = Servers.query.filter_by(location=tour.id).all()
            num_servers = len(servers)
            num_registrations = len(registrations)
            accepted_registrations = Registration.query.filter_by(tour_id=tour.id, reg_accepted=True).all()
            num_accepted = len(accepted_registrations)
            matches = None
            if os.path.exists('cargo/data/' + str(tour.id) + '.json'):
                config = json.load(open('cargo/data/' + str(tour.id) + '.json'))
                try:
                    matches = config["matches"]
                except KeyError:
                    matches = None
            return render_template('dashboard.html',
                                   user=current_user,
                                   title=tour.name,
                                   tour=tour,
                                   num_registrations=num_registrations,
                                   num_accepted=num_accepted,
                                   num_servers=num_servers,
                                   matches=matches)
        return render_template('unauth.html', user=current_user, title='Access Denied')
    return render_template('error.html', user=current_user, title='Page Not Found')


@application.route('/organise/<int:id>/settings', methods=['GET', 'POST'])
@login_required
def tournament_settings(id):
    tour = Tournament.query.get(id)
    if tour:
        if tour.admin == current_user.id:
            form = CreateTournament()
            form.submit.label.text = 'Update Details'
            if request.method == 'GET':
                form.name.data = tour.name
                form.type.data = tour.type
                form.prize.data = tour.prize
                form.max_teams.data = tour.max_teams
                reg_start = str(tour.reg_start).split("-")
                reg_start_data = datetime.datetime(int(reg_start[0]), int(reg_start[1]), int(reg_start[2]))
                form.reg_start.data = reg_start_data
                reg_end = str(tour.reg_end).split("-")
                reg_end_data = datetime.datetime(int(reg_end[0]), int(reg_end[1]), int(reg_end[2]))
                form.reg_end.data = reg_end_data
                tour_start = str(tour.tour_start).split("-")
                tour_start_data = datetime.datetime(int(tour_start[0]), int(tour_start[1]), int(tour_start[2]))
                form.tour_start.data = tour_start_data
                tour_end = str(tour.tour_end).split("-")
                tour_end_data = datetime.datetime(int(tour_end[0]), int(tour_end[1]), int(tour_end[2]))
                form.tour_end.data = tour_end_data
                form.paid.data = tour.paid
                form.payment_info.data = tour.payment_info
            if form.validate_on_submit():
                tour.name = form.name.data
                tour.type = form.type.data
                tour.prize = form.prize.data
                if not tour.third:
                    tour.max_teams = form.max_teams.data
                tour.reg_start = str(form.reg_start.data)
                tour.reg_end = str(form.reg_end.data)
                tour.tour_start = str(form.tour_start.data)
                tour.tour_end = str(form.tour_end.data)
                tour.paid = form.paid.data
                tour.payment_info = form.payment_info.data
                db.session.commit()
                save = Tournament.query.get(id)
                save_tournament(save)
                tourney_matches = TournamentBrackets(save)
                if form.type.data == 'se':
                    for i in range(8):
                        tourney_matches.single_elimination(i)
                return redirect(url_for('tournament', id=tour.id))
            return render_template('create_tournament.html', user=current_user, title='Update Tournament', form=form)


@application.route('/organise/<int:id>/registrations')
@login_required
def organiser_registrations(id):
    tour = Tournament.query.get(id)
    if tour:
        if tour.admin == current_user.id:
            participants = Registration.query.filter_by(tour_id=id).all()
            teams = []
            for participant in participants:
                reg_team = Team.query.get(participant.team_id)
                reg_team.reg_accepted = participant.reg_accepted
                teams.append(reg_team)
            return render_template('organiser_reg.html', user=current_user, teams=teams, tour=tour)
        return render_template('unauth.html', user=current_user, title='Unathorised')
    return render_template('error.html', user=current_user, title='Page Not Found')


@application.route('/organise/<tour_id>/teams_details/<int:team_id>')
@login_required
def organiser_team_details(tour_id, team_id):
    tour = Tournament.query.get(tour_id)
    if tour:
        bracket = bracket_type(tour)
        organiser = User.query.filter_by(id=tour.admin).first()
        if tour.admin == current_user.id:
            teamRegistered = Registration.query.filter_by(tour_id=tour_id, team_id=team_id).first()
            if teamRegistered:
                if teamRegistered.reg_accepted:
                    teamR = Team.query.get(teamRegistered.team_id)
                    reg_team = load_players(tour, teamR)
                    reg_team.reg_accepted = True

                else:
                    reg_team = Team.query.get(teamRegistered.team_id)
                    reg_team.reg_accepted = False
                # raise Exception
                return render_template('registered_details.html',
                                       user=current_user,
                                       title=tour.name,
                                       tour=tour, team=reg_team,
                                       bracket=bracket,
                                       organiser=organiser,
                                       admin=True)
            return render_template('error.html', title='Team Not Found', user=current_user)
        return render_template('unauth.html', title='Not the admin', user=current_user)
    return render_template('error.html', title='Tournament Not Found', user=current_user)


@application.route('/organise/<int:tour_id>/accept/<int:team_id>')
@login_required
def accept_reg(tour_id, team_id):
    tour = Tournament.query.get(tour_id)
    if tour:
        if tour.admin == current_user.id:
            reg_team = Team.query.get(team_id)
            if reg_team:
                regs = Registration.query.filter_by(tour_id=tour_id, reg_accepted=True).all()
                if len(regs) >= int(tour.max_teams):
                    flash('Registrations Full! Delete a registration to allow this team.', 'danger')
                    return redirect('/organise/' + str(tour_id) + '/registrations')
                reg = Registration.query.filter_by(tour_id=tour_id, team_id=team_id).first()
                if add_team_tournament(tour, reg_team):
                    tour.participants = tour.participants + 1
                reg.reg_accepted = True
                db.session.commit()
                tourney_matches = TournamentBrackets(tour)
                if tour.type == 'se':
                    for i in range(8):
                        tourney_matches.single_elimination(i)
            return redirect('/organise/' + str(tour_id) + '/registrations')
        return render_template('unauth.html', title='Not the admin', user=current_user)
    return render_template('error.html', title='Tournament Not Found', user=current_user)


@application.route('/organise/<int:tour_id>/delete_reg/<int:team_id>')
@login_required
def delete_reg(tour_id, team_id):
    tour = Tournament.query.get(tour_id)
    if tour:
        if tour.admin == current_user.id:
            reg_team = Team.query.get(team_id)
            if reg_team:
                reg = Registration.query.filter_by(tour_id=tour_id, team_id=team_id).first()
                my_team = Team.query.get(team_id)
                if delete_team_tournament(tour, my_team):
                    tour.participants = tour.participants - 1
                reg.reg_accepted = False
                db.session.commit()
                tourney_matches = TournamentBrackets(tour)
                if tour.type == 'se':
                    for i in range(8):
                        tourney_matches.single_elimination(i)
            return redirect('/organise/' + str(tour_id) + '/registrations')
        return render_template('unauth.html', title='Not the admin', user=current_user)
    return render_template('error.html', title='Tournament Not Found', user=current_user)

@application.route('/browse')
def browse_tournament():
    tour = Tournament.query.filter_by(reg_open=True).all()
    return render_template('browse.html', user=current_user, title='Browse', tour=tour)


@application.route('/browse/<int:id>/register')
@login_required
def tour_details(id):
    tour = Tournament.query.get(id)
    if tour:
        organiser = User.query.filter_by(id=tour.admin).first()
        my_team = Team.query.filter_by(user=current_user.id).first()
        bracket = bracket_type(tour)
        return render_template('tour_details.html', user=current_user,
                               title=tour.name,
                               tour=tour, team=my_team,
                               bracket=bracket,
                               organiser=organiser)
    return render_template('error.html', title='Page Not Found', user=current_user)


@application.route('/browse/<int:id>/register/confirm')
@login_required
def reg_confirm(id):
    tour = Tournament.query.get(id)
    if tour:
        my_team = Team.query.filter_by(user=current_user.id).first()
        if my_team:
            regs = Registration.query.filter_by(tour_id=tour.id, team_id=my_team.id).first()
            if regs:
                return redirect(url_for('registered_tournaments'))
            tour.reg_no = tour.reg_no + 1
            reg = Registration(tour_id=tour.id, team_id=my_team.id)
            db.session.add(reg)
            db.session.commit()
            return redirect(url_for('registered_tournaments'))
        return redirect('/browse/id/register')
    return render_template('error.html', title='404 Not Found', user=current_user)


@application.route('/tournaments')
@login_required
def registered_tournaments():
    my_team = Team.query.filter_by(user=current_user.id).first()
    if my_team:
        regs = Registration.query.filter_by(team_id=my_team.id).all()
        tours = []
        for reg in regs:
            tour = Tournament.query.get(reg.tour_id)
            tour.accepted = reg.reg_accepted
            tours.append(tour)
        return render_template('tournaments.html', user=current_user, title='Browse', tour=tours)
    return redirect('team')


@application.route('/tournaments/<int:id>/details')
@login_required
def registered_details(id):
    tour = Tournament.query.get(id)
    if tour:
        organiser = User.query.filter_by(id=tour.admin).first()
        my_team = Team.query.filter_by(user=current_user.id).first()
        reg = Registration.query.filter_by(tour_id=tour.id, team_id=my_team.id).first()
        if reg.reg_accepted:
            p = load_players(tour, my_team)
            if p:
                my_team = p
        bracket = bracket_type(tour)
        return render_template('registered_details.html', user=current_user,
                               title=tour.name,
                               tour=tour, team=my_team,
                               bracket=bracket,
                               organiser=organiser)
    return render_template('error.html', title='Page Not Found', user=current_user)


@application.route('/tournaments/<int:id>/withdraw')
@login_required
def withdraw(id):
    tour = Tournament.query.get(id)
    if tour:
        my_team = Team.query.filter_by(user=current_user.id).first()
        accepted = delete_team_tournament(tour, my_team)
        if accepted:
            tour.participants = tour.participants - 1
        Registration.query.filter_by(tour_id=id, team_id=my_team.id).delete()
        tour.reg_no = tour.reg_no - 1
        db.session.commit()
        return redirect(url_for('registered_tournaments'))
    return render_template('error.html', user=current_user, title='Page Not Found')


@application.route('/organise/<int:id>/add_servers', methods=['GET', 'POST'])
def add_server(id):
    tour = Tournament.query.get(id)
    if tour:
        if tour.admin == current_user.id:
            form = AddServerForm()
            if form.validate_on_submit():
                gs = GameServer(form.ip.data, form.port.data, form.password.data)
                plugin_check = gs.check_plugins()
                if plugin_check:
                    if plugin_check["get5"]:
                        server_ip = gs.server_ip()
                        plugin_check2 = gs.check_plugins()
                        if not plugin_check2:
                            server_ip = form.ip.data
                        existing_server = Servers.query.filter_by(ip=server_ip,
                                                                  port=form.port.data,
                                                                  location=tour.id).first()
                        if existing_server:
                            flash('Server already exists for this tournament', 'warning')
                            return redirect(url_for('tour_servers', id=tour.id))
                        server = Servers(hostname=form.name.data,
                                         ip=server_ip,
                                         port=form.port.data,
                                         password=form.password.data,
                                         location=tour.id,
                                         user_id=current_user.id)
                        serv_status = gs.server_status()
                        if serv_status:
                            if serv_status["gamestate"] == 0:
                                server.busy = False
                        else:
                            server.busy = True
                        db.session.add(server)
                        db.session.commit()
                    else:
                        flash("Server details incorrect or server is down", "danger")
                        return redirect(url_for('add_server'))
                    return redirect(url_for('tour_servers', id=tour.id))
                flash("Server details incorrect or server is down", "danger")
                return redirect(url_for('add_server', id=tour.id))
            return render_template('add_server_form.html', title='Add Server', form=form, user=current_user, tour=tour)
        return render_template('error.html', user=current_user, title='Page Not Found')
    return render_template('error.html', user=current_user, title='Page Not Found')


@application.route('/organise/<int:id>/servers')
@login_required
def tour_servers(id):
    tour = Tournament.query.get(id)
    if tour:
        if tour.admin == current_user.id:
            all_servers = Servers.query.filter_by(location=id).all()
            servers = []
            for server in all_servers:
                gs = GameServer(server.ip, server.port, server.password)
                status = gs.server_status()
                if status:
                    if status["gamestate"] == 0:
                        server.status = 'Online'
                    else:
                        server.status = 'Busy'
                else:
                    server.status = 'Offline'
                servers.append(server)
            return render_template('servers.html', user=current_user, servers=servers, tour=tour)
        return render_template('unauth.html', user=current_user, title='Unathorised')
    return render_template('error.html', user=current_user, title='Page Not Found')


@application.route('/organise/<int:id>/delete/<int:tour_id>')
@login_required
def del_servers(id, tour_id):
    server = Servers.query.get(id)
    if server:
        if server.user_id == current_user.id:
            Servers.query.filter_by(id=id, location=tour_id).delete()
            db.session.commit()
            return redirect(url_for('tour_servers', id=tour_id))
        return render_template('unauth.html', user=current_user, title='Unathorised')
    return render_template('error.html', user=current_user, title='Page Not Found')


@application.route('/organise/<int:tour_id>/round/<string:round_num>/match/<int:match_num>', methods=['GET', 'POST'])
@login_required
def schedule_match(tour_id, round_num, match_num):
    tour = Tournament.query.get(tour_id)
    if tour:
        if tour.admin == current_user.id:
            form = ScheduleMatch()
            if form.validate_on_submit():
                if os.path.exists('cargo/data/' + str(tour_id) + '.json'):
                    config = json.load(open('cargo/data/' + str(tour_id) + '.json'))
                    match = config["matches"][round_num][str(match_num)]
                    match["date"] = str(form.date.data)
                    match["time"] = form.time.data
                    config = json.dumps(config, indent=4)
                    with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
                        f.write(config)
                return redirect(url_for('tournament', id=tour.id))
            return render_template('schedule_match.html', user=current_user, tour=tour, form=form)
        return render_template('unauth.html', user=current_user, title='Unathorised')
    return render_template('error.html', user=current_user, title='Page Not Found')


@application.route('/matchpage/<int:matchid>/se')
@login_required
def matchpage(matchid):
    tour_id, round_num, match_num = details_from_match_id(matchid)
    tour = Tournament.query.get(tour_id)
    if tour:
        if os.path.exists('cargo/data/' + str(tour.id) + '.json'):
            config = json.load(open('cargo/data/' + str(tour.id) + '.json'))
        else:
            return render_template('error.html', user=current_user, title='Page Not Found')
        matches = config["matches"]
        if matches:
            round = matches["round" + str(round_num)]
            if round:
                match = round[str(match_num)]
            else:
                return render_template('error.html', user=current_user, title='Page Not Found')
        else:
            return render_template('error.html', user=current_user, title='Page Not Found')
    else:
        return render_template('error.html', user=current_user, title='Page Not Found')
    team1 = match["team1"]
    team2 = match["team2"]
    if team1:
        team1_id = team1["id"]
    else:
        team1_id = None
    if team2:
        team2_id = team2["id"]
    else:
        team2_id = None
    my_team = Team.query.filter_by(user=current_user.id).first()
    if my_team.id == team1_id:
        auth_token = token_hex(20)
        team1["auth_token"] = auth_token
        config = json.dumps(config, indent=4)
        with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
            f.write(config)
        return render_template('veto.html', user=current_user, title='Match Veto Page', team1=team1, team2=team2,
                               auth_token=auth_token, my_team_num=1, matchid=matchid)
    if my_team.id == team2_id:
        auth_token = token_hex(20)
        team2["auth_token"] = auth_token
        config = json.dumps(config, indent=4)
        with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
            f.write(config)
        return render_template('veto.html', user=current_user, title='Match Veto Page', team1=team1, team2=team2,
                               auth_token=auth_token, my_team_num=2, matchid=matchid)
    return render_template('unauth.html', user=current_user, title='Unathorised')


@sock.route('/matchpage')
def matchpage_sock(ws):
    while True:
        data_received = ws.receive()
        data_received = json.loads(data_received)
        matchid = int(data_received["matchid"])
        tour_id, round_num, match_num = details_from_match_id(matchid)
        tour = Tournament.query.get(tour_id)
        if tour:
            if os.path.exists('cargo/data/' + str(tour.id) + '.json'):
                config = json.load(open('cargo/data/' + str(tour.id) + '.json'))
                matches = config["matches"]
                if matches:
                    round = matches["round" + str(round_num)]
                    if round:
                        match = round[str(match_num)]
                        if match:
                            veto_data = veto_status(tour_id, round_num, match_num, data=data_received, get=False)
                            if veto_data["completed"]:
                                server = Servers.query.filter_by(ip=veto_data["serverstatus"]["ip"], port=veto_data["serverstatus"]["port"]).first()
                                if server:
                                    server.busy = True
                                    gs = GameServer(server.ip, server.port, server.password)
                                    gs.load_match(tour_id, round_num, match_num)


@sock.route('/matchdata/<int:matchid>')
def echo(ws, matchid):
    while True:
        tour_id, round_num, match_num = details_from_match_id(matchid)
        data = veto_status(tour_id, round_num, match_num, data=False, get=True)
        ws.send(json.dumps(data))
        time.sleep(1)
