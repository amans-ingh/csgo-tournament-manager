from dhooks import Webhook, Embed

wh = "https://discord.com/api/webhooks/964852305872703518/6INtbWwfM4GFJokS3S-QQLUXgSnU6TdWtKBfNnRof6j5CLrueW7z3B0S3cphAh2uf8GS"
# wh = "https://discord.com/api/webhooks/964920929224368228/xRFcJ9itdj1r8TUuL5Vp4shbvYV4-EbseVRRRPxNvqOr-RTxu3KiZFaPwLyBjJMk_6Ar"


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


def admin_server_unavailable(wh, match):
    admins = Webhook(wh)
    title = 'Server unavailable'
    description = 'No server is currently available for the the upcoming match. Please reschedule the match atleast' \
                  ' 15 minutes before the match start or else match will be automatically rescheduled at a time ' \
                  'on which a server is expected to be free.'
    fields = ['Round', 'Match', 'Tournament Name']
    values = [match.round, match.m, match.tour]
    embed = Embed(title=title, description=description, color=0xA500FF)
    for i, j in zip(fields, values):
        embed.add_field(name=i, value=j)
    admins.send(embed=embed)


class Match:
    def __init__(self):
        self.round = 2
        self.m = 1
        self.tour = "Dreams and Nightmare"


match = Match()
admin_server_unavailable(wh, match)
