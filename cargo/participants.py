import json
import os

from flask import render_template, url_for, redirect
from cargo import application, db
from cargo.models import User, Team, Tournament, Registration
from flask_login import current_user, login_required
from cargo.functions import bracket_type, delete_team_tournament, load_players
from cargo.brackets import TournamentBrackets


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
        return render_template('registered_details.html', user=current_user,
                               title=tour.name,
                               tour=tour, team=my_team,
                               bracket=bracket,
                               organiser=organiser,
                               matches=matches,
                               matchid=None,
                               tour_type='se')
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
