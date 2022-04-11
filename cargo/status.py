from flask import request
from cargo import application, db
from cargo.models import Match, Servers, MapStats, PlayerStats


@application.route('/api/match/<match_id>/finish', methods=['POST'])
def match_finished(match_id):
    match = Match.query.filter_by(id=match_id).first()
    if match:
        if match.api == request.values.get('key'):
            winner = request.values.get('winner')
            match.status = 3
            if winner == 'team1':
                match.winner = match.team1_id
            if winner == 'team2':
                match.winner = match.team2_id
            else:
                match.winner = None
            forfeit = request.values.get('forfeit', 0)
            if forfeit == 1:
                match.forfeit = True
                if winner == 'team1':
                    match.team1_score = 1
                    match.team2_score = 0
                elif winner == 'team2':
                    match.team1_score = 0
                    match.team2_score = 1
            server = Servers.query.get(match.server_id)
            if server:
                server.busy = False
            db.session.commit()
            return 'Success'
        return 'failed'
    return 'failed'


@application.route('/match/<int:match_id>/map/<int:map_number>/start', methods=['POST'])
def map_started(match_id, map_number):
    match = Match.query.get(match_id)
    if match:
        if match.api == request.values.get('key'):
            map_stats = MapStats.query.filter_by(match_id=match_id, map_number=map_number).first()
            if map_stats is None:
                map_stats = MapStats()
                db.session.add(map_stats)
            map_stats.match_id = match_id
            map_stats.map_number = map_number
            map_stats.map_name = request.values.get('mapname')
            db.session.commit()
            return 'Success'
        return 'failed', 400
    return 'failed', 400


@application.route('/match/<int:match_id>/map/<int:map_number>/update', methods=['POST'])
def map_update(match_id, map_number):
    match = Match.query.get(match_id)
    if match:
        if match.api == request.values.get('key'):
            map_stats = MapStats.query.filter_by(match_id=match_id, map_number=map_number).first()
            if map_stats is None:
                map_stats = MapStats()
                map_stats.match_id = match_id
                db.session.add(map_stats)
            t1 = int(request.values.get('team1score'))
            t2 = int(request.values.get('team2score'))
            if t1 != -1 and t2 != -1:
                map_stats.team1_score = t1
                map_stats.team2_score = t2
            db.session.commit()
            return 'Success'
        return 'failed', 400
    return 'failed', 400


@application.route('/match/<int:match_id>/map/<int:map_number>/finish', methods=['POST'])
def map_finished(match_id, map_number):
    match = Match.query.get(match_id)
    if match:
        if match.api == request.values.get('key'):
            map_stats = MapStats.query.filter_by(match_id=match_id, map_number=map_number).first()
            if map_stats:
                winner = request.values.get('winner')
                if winner == 'team1':
                    map_stats.winner = match.team1_id
                    match.team1_score += 1
                if winner == 'team2':
                    map_stats.winner = match.team2_id
                    match.team2_score += 1
            else:
                return 'failed to find map stats object', 400
            db.session.commit()
            return 'Success'
        return 'failed', 400
    return 'failed', 400


@application.route('/match/<int:match_id>/map/<int:map_number>/player/<steamid64>/update', methods=['POST'])
def players_stats(match_id, map_number, steamid64):
    match = Match.query.get(match_id)
    if match:
        if match.api == request.values.get('key'):
            map_stats = MapStats.query.filter_by(match_id=match_id, map_number=map_number).first()
            if map_stats:
                player_stats = PlayerStats.query.filter_by(match_id=match_id, steam_id=steamid64).first()
                if player_stats is None:
                    player_stats = PlayerStats()
                    db.session.add(player_stats)
                player_stats.name = request.values.get('name')
                team = request.values.get('team')
                if team == 'team1':
                    player_stats.team_id = match.team1_id
                elif team == 'team2':
                    player_stats.team_id = match.team2_id
                player_stats.steam_id = steamid64
                player_stats.kills = int(request.values.get('kills'))
                player_stats.assists = int(request.values.get('assists'))
                player_stats.deaths = int(request.values.get('deaths'))
                player_stats.flashbang_assists = int(request.values.get('flashbang_assists'))
                player_stats.teamkills = int(request.values.get('teamkills'))
                player_stats.suicides = int(request.values.get('suicides'))
                player_stats.damage = int(request.values.get('damage'))
                player_stats.headshot_kills = int(request.values.get('headshot_kills'))
                player_stats.roundsplayed = int(request.values.get('roundsplayed'))
                player_stats.bomb_plants = int(request.values.get('bomb_plants'))
                player_stats.bomb_defuses = int(request.values.get('bomb_defuses'))
                player_stats.k1 = int(request.values.get('1kill_rounds'))
                player_stats.k2 = int(request.values.get('2kill_rounds'))
                player_stats.k3 = int(request.values.get('3kill_rounds'))
                player_stats.k4 = int(request.values.get('4kill_rounds'))
                player_stats.k5 = int(request.values.get('5kill_rounds'))
                player_stats.v1 = int(request.values.get('v1'))
                player_stats.v2 = int(request.values.get('v2'))
                player_stats.v3 = int(request.values.get('v3'))
                player_stats.v4 = int(request.values.get('v4'))
                player_stats.v5 = int(request.values.get('v5'))
                player_stats.firstkill_t = int(request.values.get('firstkill_t'))
                player_stats.firstkill_ct = int(request.values.get('firstkill_ct'))
                player_stats.firstdeath_t = int(request.values.get('firstdeath_t'))
                player_stats.firstdeath_Ct = int(request.values.get('firstdeath_ct'))
                db.session.commit()
            else:
                return 'failed to find map stats object', 400
            return 'Success'
        return 'failed', 400
    return 'failed', 400
