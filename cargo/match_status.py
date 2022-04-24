from cargo import application, db
from cargo.brackets import TournamentBrackets
from cargo.functions import details_from_match_id
from cargo.models import Match, MapStats, PlayerStats, Servers, Tournament
from flask import request


def as_int(val, on_fail=0):
    if val is None:
        return on_fail
    try:
        return int(val)
    except ValueError:
        return on_fail


def match_api_check(request, match):
    if match.api_key != request.values.get('key'):
        return None

    # if match.finalized():
    #     return None
    return True


@application.route('/match/<int:matchid>/finish', methods=['POST'])
def match_finish(matchid):
    match = Match.query.filter_by(matchid=matchid).first()
    tour = Tournament.query.get(match.tour)
    tb = TournamentBrackets(tour)
    tour_id, round_num, match_num = details_from_match_id(matchid)
    if not match:
        return "Invalid matchid", 404
    if not match_api_check(request, match):
        return "Wrong API Key", 404

    winner = request.values.get('winner')
    if winner == 'team1':
        match.winner = match.team1_id
        tb.single_elimination(round_num, {"match": str(match_num), "winnerId": match.winner})
        tb.single_elimination(round_num+1)
    elif winner == 'team2':
        match.winner = match.team2_id
        tb.single_elimination(round_num, {"match": str(match_num), "winnerId": match.winner})
        tb.single_elimination(round_num+1)
    else:
        match.winner = None
    forfeit = request.values.get('forfeit', 0)
    if forfeit == 1:
        match.forfeit = True
        # Reassign scores
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


@application.route('/match/<int:matchid>/map/<int:mapnumber>/start', methods=['POST'])
def match_map_start(matchid, mapnumber):
    match = Match.query.filter_by(matchid=matchid).first()
    if not match:
        return "Invalid matchid", 404
    if not match_api_check(request, match):
        return "Wrong API Key", 404

    map_name = request.values.get('mapname')

    # Create mapstats object if needed
    MapStats.get_or_create(matchid, mapnumber, map_name)
    db.session.commit()

    return 'Success'


@application.route('/match/<int:matchid>/map/<int:mapnumber>/update', methods=['POST'])
def match_map_update(matchid, mapnumber):
    match = Match.query.filter_by(matchid=matchid).first()
    if not match:
        return "Invalid matchid", 404
    if not match_api_check(request, match):
        return "Wrong API Key", 404

    map_stats = MapStats.query.filter_by(match_id=matchid, map_number=mapnumber).first()
    if map_stats:
        t1 = as_int(request.values.get('team1score'))
        t2 = as_int(request.values.get('team2score'))
        if t1 != -1 and t2 != -1:
            map_stats.team1_score = t1
            map_stats.team2_score = t2
            db.session.commit()
    else:
        return 'Failed to find map stats object', 400

    return 'Success'


@application.route('/match/<int:matchid>/map/<int:mapnumber>/finish', methods=['POST'])
def match_map_finish(matchid, mapnumber):
    match = Match.query.filter_by(matchid=matchid).first()
    if not match:
        return "Invalid matchid", 404
    if not match_api_check(request, match):
        return "Wrong API Key", 404

    map_stats = MapStats.query.filter_by(match_id=matchid, map_number=mapnumber).first()
    if map_stats:

        winner = request.values.get('winner')
        if winner == 'team1':
            map_stats.winner = match.team1_id
            match.team1_score += 1
        elif winner == 'team2':
            map_stats.winner = match.team2_id
            match.team2_score += 1
        else:
            map_stats.winner = None

        db.session.commit()
    else:
        return 'Failed to find map stats object', 404

    return 'Success'


@application.route(
    '/match/<int:matchid>/map/<int:mapnumber>/player/<steamid64>/update',
    methods=['POST'])
def match_map_update_player(matchid, mapnumber, steamid64):
    match = Match.query.filter_by(matchid=matchid).first()
    if not match:
        return "Invalid matchid", 404
    api_key = request.values.get('key')
    if match.api_key != api_key:
        return 'Wrong API key', 400

    map_stats = MapStats.query.filter_by(match_id=matchid, map_number=mapnumber).first()
    if map_stats:
        player_stats = PlayerStats.get_or_create(matchid, mapnumber, steamid64)
        if player_stats:
            player_stats.name = request.values.get('name')
            team = request.values.get('team')
            if team == 'team1':
                player_stats.team_id = match.team1_id
            elif team == 'team2':
                player_stats.team_id = match.team2_id

            player_stats.kills = as_int(request.values.get('kills'))
            player_stats.assists = as_int(request.values.get('assists'))
            player_stats.deaths = as_int(request.values.get('deaths'))
            player_stats.flashbang_assists = as_int(
                request.values.get('flashbang_assists'))
            player_stats.teamkills = as_int(request.values.get('teamkills'))
            player_stats.suicides = as_int(request.values.get('suicides'))
            player_stats.damage = as_int(request.values.get('damage'))
            player_stats.headshot_kills = as_int(
                request.values.get('headshot_kills'))
            player_stats.roundsplayed = as_int(
                request.values.get('roundsplayed'))
            player_stats.bomb_plants = as_int(
                request.values.get('bomb_plants'))
            player_stats.bomb_defuses = as_int(
                request.values.get('bomb_defuses'))
            player_stats.k1 = as_int(request.values.get('1kill_rounds'))
            player_stats.k2 = as_int(request.values.get('2kill_rounds'))
            player_stats.k3 = as_int(request.values.get('3kill_rounds'))
            player_stats.k4 = as_int(request.values.get('4kill_rounds'))
            player_stats.k5 = as_int(request.values.get('5kill_rounds'))
            player_stats.v1 = as_int(request.values.get('v1'))
            player_stats.v2 = as_int(request.values.get('v2'))
            player_stats.v3 = as_int(request.values.get('v3'))
            player_stats.v4 = as_int(request.values.get('v4'))
            player_stats.v5 = as_int(request.values.get('v5'))
            player_stats.firstkill_t = as_int(
                request.values.get('firstkill_t'))
            player_stats.firstkill_ct = as_int(
                request.values.get('firstkill_ct'))
            player_stats.firstdeath_t = as_int(
                request.values.get('firstdeath_t'))
            player_stats.firstdeath_ct = as_int(
                request.values.get('firstdeath_ct'))

            db.session.commit()
    else:
        return 'Failed to find map stats object', 404

    return 'Success'


@application.route('/match/<int:matchid>/map/<int:map_num>/demo', methods=['POST'])
def map_demo(matchid, map_num):
    match = Match.query.filter_by(matchid=matchid).first()
    if not match:
        return "Invalid matchid", 404
    api_key = request.values.get('key')
    if match.api_key != api_key:
        return 'Wrong API key', 400
    demofile = request.values.get('demoFile')
    return 'Success'
