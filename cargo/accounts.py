from flask import render_template, url_for, flash, redirect, request
from cargo import application, bcrypt, db
from cargo.models import User, Team
from cargo.forms import RegistrationForm, LoginForm, RegisterTeamForm, ChangePassword
from flask_login import login_user, current_user, logout_user, login_required


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
    my_team = Team.query.filter_by(user=current_user.id).first()
    if form.validate_on_submit():
        if my_team:
            my_team.name = form.name.data
            my_team.p1 = form.player1.data
            my_team.p1_steam_id = form.player1_steam.data
            my_team.p2 = form.player2.data
            my_team.p2_steam_id = form.player2_steam.data
            my_team.p3 = form.player3.data
            my_team.p3_steam_id = form.player3_steam.data
            my_team.p4 = form.player4.data
            my_team.p4_steam_id = form.player4_steam.data
            my_team.p5 = form.player5.data
            my_team.p5_steam_id = form.player5_steam.data
            my_team.p6 = form.player6.data
            my_team.p6_steam_id = form.player6_steam.data
            my_team.p7 = form.player7.data
            my_team.p7_steam_id = form.player7_steam.data
            my_team.p8 = form.player8.data
            my_team.p8_steam_id = form.player8_steam.data
        else:
            my_team = Team(user=current_user.id,
                           name=form.name.data,
                           p1=form.player1.data,
                           p1_steam_id=form.player1_steam.data,
                           p2=form.player2.data,
                           p2_steam_id=form.player2_steam.data,
                           p3=form.player3.data,
                           p3_steam_id=form.player3_steam.data,
                           p4=form.player4.data,
                           p4_steam_id=form.player4_steam.data,
                           p5=form.player5.data,
                           p5_steam_id=form.player5_steam.data,
                           p6=form.player6.data,
                           p6_steam_id=form.player6_steam.data,
                           p7=form.player7.data,
                           p7_steam_id=form.player7_steam.data,
                           p8=form.player8.data,
                           p8_steam_id=form.player8_steam.data)
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
