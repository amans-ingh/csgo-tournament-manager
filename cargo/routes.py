from flask import render_template, url_for, flash, redirect, request
from cargo import application, bcrypt, db
from cargo.models import User, Team, Tournament, Registration
from cargo.steamapi import SteamAPI
from cargo.forms import RegistrationForm, LoginForm, RegisterTeamForm, ChangePassword, CreateTournament
from flask_login import login_user, current_user, logout_user, login_required
from cargo.functions import bracket_type, save_tournament, add_team_tournament, delete_team_tournament, load_players
from cargo.brackets import TournamentBrackets
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
        return render_template('organiser_dashboard.html', page='match_history', user=current_user,
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
            return redirect(url_for('organise_tournament'))
        return render_template('create_tournament.html', user=current_user, title='Create Tournament', form=form)


@application.route('/organise/<int:id>/dashboard')
@login_required
def tournament(id):
    tour = Tournament.query.filter_by(id=id).first()
    if tour:
        if tour.admin == current_user.id:
            registrations = Registration.query.filter_by(tour_id=tour.id).all()
            num_registrations = len(registrations)
            accepted_registrations = Registration.query.filter_by(tour_id=tour.id, reg_accepted=True).all()
            num_accepted = len(accepted_registrations)
            return render_template('dashboard.html',
                                   user=current_user,
                                   title=tour.name,
                                   tour=tour,
                                   num_registrations=num_registrations,
                                   num_accepted=num_accepted)
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
                return redirect(url_for('organise_tournament'))
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
        reg_team = Team.query.get(team_id)
        if reg_team:
            reg = Registration.query.filter_by(tour_id=tour_id, team_id=team_id).first()
            if add_team_tournament(tour, reg_team):
                tour.participants = tour.participants + 1
            reg.reg_accepted = True
            db.session.commit()
        return redirect('/organise/' + str(tour_id) + '/registrations')


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


@application.route('/test')
def test():
    tour = Tournament.query.get(2)
    a = TournamentBrackets(tour)
    a.single_elimination(0, result={"match":0, "winnerId":1})
    a.single_elimination(1)
    a.single_elimination(2)
    return 'ok'