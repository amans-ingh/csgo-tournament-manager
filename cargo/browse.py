from flask import render_template, url_for, redirect
from cargo import application, db
from cargo.models import User, Team, Tournament, Registration
from flask_login import current_user, login_required
from cargo.functions import bracket_type


@application.route('/browse')
@login_required
def browse_tournament():
    tour = Tournament.query.filter_by(reg_open=True).all()
    tours = []
    for t in tour:
        if t.status:
            tours.append(t)
    return render_template('browse.html', user=current_user, title='Browse', tour=tours)


@application.route('/browse/<int:id>/register')
@login_required
def tour_details(id):
    tour = Tournament.query.get(id)
    if tour and tour.status:
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
    if tour and tour.status:
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
