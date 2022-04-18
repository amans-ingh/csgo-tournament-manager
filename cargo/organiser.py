import json
import os

from flask import render_template, url_for, flash, redirect, request
from cargo import application, db
from cargo.models import User, Team, Tournament, Registration, Servers
from cargo.rcon import GameServer
from cargo.forms import CreateTournament, AddServerForm, ScheduleMatch
from flask_login import current_user, login_required
from cargo.functions import bracket_type, save_tournament, add_team_tournament, delete_team_tournament, load_players
from cargo.brackets import TournamentBrackets
import datetime

from cargo.sheduling import schedule_match_events, unschedule_match_events


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
                                    reg_start_time=form.reg_start_time.data,
                                    reg_end_time=form.reg_end_time.data,
                                    admin_wh=form.admin_wh.data,
                                    players_wh=form.players_wh.data,
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
                    tb = TournamentBrackets(tour)
                    for i in range(8):
                        tb.single_elimination(i)
                    if os.path.exists('cargo/data/' + str(tour.id) + '.json'):
                        config = json.load(open('cargo/data/' + str(tour.id) + '.json'))
                        matches = config["matches"]
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
                form.reg_start_time.data = tour.reg_start_time
                reg_end = str(tour.reg_end).split("-")
                reg_end_data = datetime.datetime(int(reg_end[0]), int(reg_end[1]), int(reg_end[2]))
                form.reg_end.data = reg_end_data
                form.reg_end_time.data = tour.reg_end_time
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
                tour.reg_start_time = form.reg_start_time.data
                tour.reg_end_time = form.reg_end_time.data
                tour.admin_wh = form.admin_wh.data
                tour.rules = form.rules.data
                tour.players_wh = form.players_wh.data
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
                        other_servers = Servers.query.filter_by(ip=server_ip, port=form.port.data).all()
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
                                for ser in other_servers:
                                    ser.busy = False
                            else:
                                server.busy = True
                                for ser in other_servers:
                                    ser.busy = True
                        else:
                            server.busy = True
                            for ser in other_servers:
                                ser.busy = True
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
                db.session.commit()
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
                    unschedule_match_events(tour_id, round_num, match_num)
                    schedule_match_events(tour_id, round_num, match_num)
                return redirect(url_for('tournament', id=tour.id))
            return render_template('schedule_match.html', user=current_user, tour=tour, form=form)
        return render_template('unauth.html', user=current_user, title='Unathorised')
    return render_template('error.html', user=current_user, title='Page Not Found')
