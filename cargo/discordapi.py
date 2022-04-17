import json
import os
from dhooks import Webhook, Embed
from cargo import application, db
from cargo.brackets import TournamentBrackets
from cargo.models import Tournament


def admin_webhook_server_issue(wh, server_name, server_ip, server_port):
    admins = Webhook(wh)
    title = 'Server not responding'
    description = 'The following mentioned server is not responding due to unknown reasons. Please ensure that server' \
                  ' is online, with all the required plugins and its RCON password is correct.'
    fields = ['Server name', 'IP Address', 'Port']
    values = [server_name, server_ip, server_port]
    embed = Embed(title=title, description=description, color=0xA500FF)
    for i, j in zip(fields, values):
        embed.add_field(name=i, value=j)
    admins.send(embed=embed)


def admin_server_unavailable(tour, round_num, match_num):
    admins = Webhook(tour.admin_wh)
    title = 'Server unavailable'
    description = 'No server is currently available for the the upcoming match. Please reschedule the match atleast' \
                  ' 15 minutes before the match start or else match will be automatically rescheduled at a time ' \
                  'on which a server is expected to be free.'
    fields = ['Round', 'Match', 'Tournament Name']
    values = [round_num, match_num, tour.name]
    embed = Embed(title=title, description=description, color=0xA500FF)
    for i, j in zip(fields, values):
        embed.add_field(name=i, value=j)
    admins.send(embed=embed)


def participant_map_veto(tour, round_num, match_num):
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
    tb = TournamentBrackets(tour)
    if team1 and not team2:
        tb.single_elimination(round=round_num, result=team1["id"])
    if team2 and not team1:
        tb.single_elimination(round=round_num, result=team2["id"])
    if not team1 and not team2:
        pass
    if team1 and team2:
        if tour.players_wh:
            participants = Webhook(tour.players_wh)
            title = team1["name"] + ' vs ' + team2["name"]
            description = 'Captains of both the teams are required to join the map veto for their upcoming match ' \
                          'on the ' \
                          'given link. Please join the veto otherwise your opponent will be declared as winner.'
            fields = ['Veto Page Link']
            r_n = round_num.split("round")
            matchid = 2048*(int(tour.id)+1) + 256*(int(r_n[1])+1) + (match_num + 1)
            values = [application.config["SERVER_URL"]+'/matchpage/' + str(matchid) + '/se']
            embed = Embed(title=title, description=description, color=0xA500FF)
            for i, j in zip(fields, values):
                embed.add_field(name=i, value=j)
            participants.send(embed=embed)
            tourna = Tournament.query.get(tour.id)
            tourna.third=True
            match["veto"] = True
            match["matchid"] = matchid
            config = json.dumps(config, indent=4)
            with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
                f.write(config)
            db.session.commit()
