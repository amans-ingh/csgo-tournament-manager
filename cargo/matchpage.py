import json
import os
import time

from flask import render_template
from cargo import application, db, sock
from cargo.models import Team, Tournament, Servers, Match
from cargo.rcon import GameServer
from flask_login import current_user, login_required
from cargo.functions import details_from_match_id, veto_status
from secrets import token_hex


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
                try:
                    match = round[str(match_num)]
                    veto = match["veto"]
                    if not veto:
                        return render_template('error.html', user=current_user, title='Page Not Found')
                except:
                    return render_template('error.html', user=current_user, title='Page Not Found')
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
    if my_team:
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
                                veto = match["veto"]
                                if not veto:
                                    return
                                veto_data = veto_status(tour_id, round_num, match_num, data=data_received, get=False)
                                if veto_data["completed"]:
                                    server = Servers.query.filter_by(ip=veto_data["serverstatus"]["ip"], port=veto_data["serverstatus"]["port"]).first()
                                    if server:
                                        api_key = token_hex(20)
                                        server.busy = True
                                        gs = GameServer(server.ip, server.port, server.password)
                                        matchdb = Match.query.filter_by(matchid=matchid).first()
                                        if matchdb:
                                            matchdb.tour = tour_id
                                            matchdb.round_num = round_num
                                            matchdb.match_num = match_num
                                            matchdb.api_key = api_key
                                            matchdb.server_id = server.id
                                            matchdb.ip = server.ip
                                            matchdb.team1_id = match["team"]["id"]
                                            matchdb.tea2_id = match["team2"]["id"]
                                            db.session.commit()
                                            gs.load_match(tour_id, round_num, match_num)
                                            return
                                        matchdb = Match(tour=tour_id,
                                                        round_num=round_num,
                                                        match_num=match_num,
                                                        matchid=matchid,
                                                        api_key=api_key,
                                                        server_id=server.id,
                                                        ip=server.ip,
                                                        team1_id=match["team1"]["id"],
                                                        team2_id=match["team2"]["id"])
                                        db.session.add(matchdb)
                                        db.session.commit()
                                        gs.load_match(tour_id, round_num, match_num)
                                        return
    except ConnectionError:
        pass


@sock.route('/matchdata/<int:matchid>')
def echo(ws, matchid):
    while True:
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
                            veto = match["veto"]
                            if not veto:
                                return
        data = veto_status(tour_id, round_num, match_num, data=False, get=True)
        ws.send(json.dumps(data))
        time.sleep(1)
