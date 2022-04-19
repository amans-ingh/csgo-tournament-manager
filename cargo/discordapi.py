import json

from dhooks import Webhook, Embed
from cargo import application
import requests


def check_discord_webhook(wh):
    wh = wh.split("https://discord.com/api/webhooks/")[-1]
    data = requests.get("https://discord.com/api/webhooks/" + wh)
    try:
        json_data = data.json()
        token = json_data["token"]
        return True
    except:
        return False


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


def participants_join_veto(tour, team1, team2, matchid):
    participants = Webhook(tour.players_wh)
    title = team1["name"] + ' vs ' + team2["name"]
    description = 'Captains of both the teams are required to join the map veto for their upcoming match ' \
                  'on the ' \
                  'given link. Please join the veto otherwise your opponent will be declared as winner.'
    fields = ['Veto Page Link']
    values = [application.config["SERVER_URL"] + '/matchpage/' + str(matchid) + '/se']
    embed = Embed(title=title, description=description, color=0xA500FF)
    for i, j in zip(fields, values):
        embed.add_field(name=i, value=j)
    participants.send(embed=embed)


def admin_server_unavailable(tour, round_num, match_num):
    admins = Webhook(tour.admin_wh)
    title = 'Server unavailable'
    description = 'No server is currently available for the the upcoming match. Please add a free server' \
                  ' and reschedule the match.'
    fields = ['Round', 'Match', 'Tournament Name']
    values = [round_num, match_num, tour.name]
    embed = Embed(title=title, description=description, color=0xA500FF)
    for i, j in zip(fields, values):
        embed.add_field(name=i, value=j)
    admins.send(embed=embed)
