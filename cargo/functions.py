import json
import os

from cargo import db
from cargo.brackets import TournamentBrackets
from cargo.discordapi import participants_join_veto, admin_server_unavailable
from cargo.models import Servers, Tournament
from cargo.rcon import GameServer


class MyClass:
    def __init__(self):
        self.array = []
        self.avail_maps = []
        self.num_maps = 0
        self.map_name = []
        self.weight = 0

    def maps(self, i):
        if i >= 1:
            self.maps(i // 2)
            self.array.append(i % 2)
        m = []
        for j in range(7 - len(self.array)):
            m.append(0)
        for k in self.array:
            m.append(k)
        return m

    def maps_left(self, array):
        for i in array:
            if i:
                self.num_maps = self.num_maps + 1
        return self.num_maps

    def maps_names(self, i):
        array = self.maps(i)
        if array[0]:
            self.map_name.append('train')
        if array[1]:
            self.map_name.append('vertigo')
        if array[2]:
            self.map_name.append('nuke')
        if array[3]:
            self.map_name.append('overpass')
        if array[4]:
            self.map_name.append('dust2')
        if array[5]:
            self.map_name.append('inferno')
        if array[6]:
            self.map_name.append('mirage')
        return self.map_name

    def weight_of_map(self, name):
        if name == 'mirage':
            self.weight = 1
        if name == 'inferno':
            self.weight = 2
        if name == 'dust2':
            self.weight = 4
        if name == 'overpass':
            self.weight = 8
        if name == 'nuke':
            self.weight = 16
        if name == 'vertigo':
            self.weight = 32
        if name == 'train':
            self.weight = 64
        return self.weight


def bracket_type(tour):
    if tour.type == 'se':
        bracket = 'Single Elimination'
    elif tour.type == 'de':
        bracket = 'Double Elimination'
    elif tour.type == 'rr':
        bracket = 'Round Robin'
    else:
        bracket = 'Not yet Decided'
    return bracket


def save_tournament(tours):
    if os.path.exists('cargo/data/' + str(tours.id) + '.json'):
        tournament = json.load(open('cargo/data/' + str(tours.id) + '.json'))
    else:
        tournament = {'basic': {}, 'teams': [], 'matches': {}}
    tournament['basic']['id'] = tours.id
    tournament['basic']['name'] = tours.name
    tournament['basic']['prize'] = tours.prize
    tournament['basic']['reg_end'] = tours.reg_end
    tournament['basic']['reg_start'] = tours.reg_start
    tournament['basic']['tour_start'] = tours.tour_start
    tournament['basic']['tour_end'] = tours.tour_end
    t = json.dumps(tournament, indent=4)
    with open('cargo/data/' + str(tours.id) + '.json', 'w+') as f:
        f.write(t)


def add_round_matches(tours, round):
    if os.path.exists('cargo/data/' + str(tours.id) + '.json'):
        tournament = json.load(open('cargo/data/' + str(tours.id) + '.json'))
        total_rounds = 0
        for i in range(8):
            if tours.max_teams <= 2 ** i:
                break
            total_rounds = total_rounds + 1
        matches = tournament['matches'][round]

        seeds = []
        for teams in range(tours.max_teams):
            seeds.append({})
        for teams in tournament['teams']:
            seeds[teams['seed']] = teams

        matches_in_round = []
        for match_number in range(2 ** (total_rounds - round - 1)):
            matches_in_round.append(
                {'team1': seeds[match_number], 'team2': seeds[int(tours.max_teams) - 1 - match_number],
                 'winner': 'team1'})
            matches_in_round[match_number]['team1']['winner'] = False
            matches_in_round[match_number]['team2']['winner'] = False
            matches_in_round[match_number]['matchid'] = 0
            matches.append(matches_in_round)
        tournament['matches'][round] = matches
        t = json.dumps(tournament, indent=4)
        with open('cargo/data/' + str(tours.id) + '.json', 'w+') as f:
            f.write(t)


def add_team_tournament(tours, reg_team):
    if os.path.exists('cargo/data/' + str(tours.id) + '.json'):
        config = json.load(open('cargo/data/' + str(tours.id) + '.json'))
        for team in config['teams']:
            if team['id'] == reg_team.id:
                return False
        config['teams'].append({'name': reg_team.name,
                                'id': reg_team.id,
                                'players': {reg_team.p1_steam_id: reg_team.p1,
                                            reg_team.p2_steam_id: reg_team.p2,
                                            reg_team.p3_steam_id: reg_team.p3,
                                            reg_team.p4_steam_id: reg_team.p4,
                                            reg_team.p5_steam_id: reg_team.p5,
                                            }})
        con = json.dumps(config, indent=4)
        with open('cargo/data/' + str(tours.id) + '.json', 'w+') as f:
            f.write(con)
        return True


def delete_team_tournament(tour, reg_team):
    if os.path.exists('cargo/data/' + str(tour.id) + '.json'):
        config = json.load(open('cargo/data/' + str(tour.id) + '.json'))
        for team in config['teams']:
            if int(team['id']) == int(reg_team.id):
                config['teams'].remove(team)
                con = json.dumps(config, indent=4)
                with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
                    f.write(con)
                return True
        return False
    return False


def load_players(tour, reg_team):
    if os.path.exists('cargo/data/' + str(tour.id) + '.json'):
        config = json.load(open('cargo/data/' + str(tour.id) + '.json'))
        for team in config['teams']:
            if team['id'] == reg_team.id:
                steam_id = []
                nicknames = []
                for key in team['players']:
                    steam_id.append(key)
                    nicknames.append(team['players'][key])
                for i in range(1, 6):
                    try:
                        exec("reg_team.p" + str(i) + " = nicknames[" + str(i-1) + "]")
                        exec("reg_team.p" + str(i) + "_steam_id = steam_id[" + str(i - 1) + "]")
                    except IndexError:
                        exec("reg_team.p" + str(i) + " = None")
                        exec("reg_team.p" + str(i) + "_steam_id = None")
                return reg_team
        return False
    return False


def details_from_match_id(match_id):
    tour_id = int(match_id/2048) - 1
    match_id = match_id - 2048*(tour_id+1)
    round_num = int(match_id/256) - 1
    match_id = match_id - 256*(round_num + 1)
    match_num = match_id - 1
    return tour_id, round_num, match_num


def veto_status(tour_id, round_num, match_num, data=False, get=True):
    data_def = {
        "mapstatus": {
            "mirage": True,
            "inferno": True,
            "overpass": True,
            "dust2": True,
            "vertigo": True,
            "train": True,
            "nuke": True
        },
        "serverstatus": {
            "ip": None,
            "port": None
        },
        "voting": 1,
        "action": "Ban",
        "bo": 1,
        "team1_online": False,
        "team2_online": False,
        "completed": False
    }
    if os.path.exists('cargo/data/' + str(tour_id) + '.json'):
        config = json.load(open('cargo/data/' + str(tour_id) + '.json'))
        if config:
            matches = config["matches"]
            if matches:
                round = matches["round"+str(round_num)]
                if round:
                    match = round[str(match_num)]
                    if match:
                        if get:
                            try:
                                veto_data = match["vetostatus"]
                                return veto_data
                            except KeyError:
                                match["vetostatus"] = data_def
                                con = json.dumps(config, indent=4)
                                with open('cargo/data/' + str(tour_id) + '.json', 'w+') as f:
                                    f.write(con)
                                return data_def
                        else:
                            if data:
                                if data["auth_token"] == match["team"+str(data["team"])]["auth_token"]:
                                    try:
                                        banned_map = data["map"]
                                        veto_data = match["vetostatus"]
                                        if str(data["team"]) == str(veto_data["voting"]):
                                            veto_data["mapstatus"][banned_map] = False
                                            count = 0
                                            for maps in veto_data["mapstatus"]:
                                                if veto_data["mapstatus"][maps] == True:
                                                    count += 1
                                            if count == 1:
                                                veto_data["completed"] = True
                                            veto_data["voting"] = (int(veto_data["voting"])<<1) % 3
                                            con = json.dumps(config, indent=4)
                                            with open('cargo/data/' + str(tour_id) + '.json', 'w+') as f:
                                                f.write(con)
                                        return veto_data
                                    except KeyError:
                                        match["vetostatus"] = data_def
                                        banned_map = data["map"]
                                        veto_data = data_def
                                        if data["team"] == veto_data["voting"]:
                                            veto_data["mapstatus"][banned_map] = False
                                            count = 0
                                            for maps in veto_data["mapstatus"]:
                                                if veto_data["mapstatus"][maps] == True:
                                                    count += 1
                                            if count == 1:
                                                veto_data["completed"] = True
                                            veto_data["voting"] = (int(veto_data["voting"])<<1) % 3
                                            con = json.dumps(config, indent=4)
                                            with open('cargo/data/' + str(tour_id) + '.json', 'w+') as f:
                                                f.write(con)
                                        return veto_data
    return True


def participant_map_veto(tour, round_num, match_num):
    data_def = {
        "mapstatus": {
            "mirage": True,
            "inferno": True,
            "overpass": True,
            "dust2": True,
            "vertigo": True,
            "train": True,
            "nuke": True
        },
        "serverstatus": {
            "ip": None,
            "port": None
        },
        "voting": 1,
        "action": "Ban",
        "bo": 1,
        "team1_online": False,
        "team2_online": False,
        "completed": False
    }
    if os.path.exists('cargo/data/' + str(tour.id) + '.json'):
        config = json.load(open('cargo/data/' + str(tour.id) + '.json'))
    else:
        return False
    if config:
        matches = config["matches"]
    else:
        return False
    if matches:
        roundData = matches[str(round_num)]
    else:
        return False
    if roundData:
        match = roundData[str(match_num)]
    else:
        return False
    if match:
        team1 = match["team1"]
        team2 = match["team2"]
    else:
        return False
    r_n = round_num.split("round")
    matchid = 2048 * (int(tour.id) + 1) + 256 * (int(r_n[1]) + 1) + (match_num + 1)
    check_all_servers(tour.id)
    server = Servers.query.filter_by(location=tour.id, busy=False).first()
    if not server:
        match["veto"] = False
        match["matchid"] = matchid
        config = json.dumps(config, indent=4)
        with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
            f.write(config)
        admin_server_unavailable(tour, round_num, match_num)
        db.session.commit()
        return False
    tb = TournamentBrackets(tour)
    if team1 and not team2:
        tb.single_elimination(round=round_num, result=team1["id"])
    if team2 and not team1:
        tb.single_elimination(round=round_num, result=team2["id"])
    if not team1 and not team2:
        pass
    if team1 and team2:
        if tour.players_wh:
            participants_join_veto(tour, team1, team2, matchid)
            tourna = Tournament.query.get(tour.id)
            tourna.third=True
            match["veto"] = True
            match["matchid"] = matchid
            match["vetostatus"] = data_def
            match["vetostatus"]["serverstatus"]["ip"] = server.ip
            match["vetostatus"]["serverstatus"]["port"] = server.port
            server.busy = True
            db.session.commit()
    config = json.dumps(config, indent=4)
    with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
        f.write(config)
    db.session.commit()


def check_all_servers(tour_id):
    servers = Servers.query.filter_by(location=tour_id).all()
    for server in servers:
        gs = GameServer(server.ip, server.port, server.password)
        server_status = gs.server_status()
        if server_status:
            if server_status["gamestate"] == 0:
                server.busy = False
            else:
                server.busy = True
        else:
            server.busy = True
    db.session.commit()
