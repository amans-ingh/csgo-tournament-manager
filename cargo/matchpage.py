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
    server_url = application.config["SERVER_URL"]
    if "https" in server_url:
        protocol = 'wss'
        server_url = str(server_url).replace("https://", '')
    else:
        protocol = 'ws'
        server_url = server_url.replace("http://", '')
    my_team = Team.query.filter_by(user=current_user.id).first()
    if my_team.id == team1_id:
        auth_token = token_hex(20)
        team1["auth_token"] = auth_token
        config = json.dumps(config, indent=4)
        with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
            f.write(config)
        return render_template('veto.html', user=current_user, title='Match Veto Page', team1=team1, team2=team2,
                               auth_token=auth_token, my_team_num=1, matchid=matchid, protocol=protocol,
                               server_url=server_url)
    if my_team.id == team2_id:
        auth_token = token_hex(20)
        team2["auth_token"] = auth_token
        config = json.dumps(config, indent=4)
        with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
            f.write(config)
        return render_template('veto.html', user=current_user, title='Match Veto Page', team1=team1, team2=team2,
                               auth_token=auth_token, my_team_num=2, matchid=matchid, protocol=protocol,
                               server_url=server_url)
    return render_template('unauth.html', user=current_user, title='Unathorised')


@sock.route('/matchpage')
def matchpage_sock(ws):
    try:
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
    except:
        pass


@sock.route('/matchdata/<int:matchid>')
def echo(ws, matchid):
    try:
        while True:
            tour_id, round_num, match_num = details_from_match_id(matchid)
            data = veto_status(tour_id, round_num, match_num, data=False, get=True)
            ws.send(json.dumps(data))
            time.sleep(1)
    except:
        pass