import json
import os
from cargo.models import Registration

class TournamentBrackets:
    def __init__(self, tournament):
        self.tour = tournament

    def single_elimination(self, winner=None):
        if os.path.exists('cargo/data/' + str(self.tour.id) + '.json'):
            config = json.load(open('cargo/data/' + str(self.tour.id) + '.json'))
            try:
                number_of_rounds = config['basic']['total_rounds_se']
            except KeyError:
                number_of_rounds = 0
                for i in range(8):
                    if self.tour.max_teams <= 2 ** i:
                        print(i)
                        break
                    number_of_rounds = number_of_rounds + 1
                config['basic']['total_rounds_se'] = number_of_rounds
            total_positions = 2**int(config['basic']['total_rounds_se'])
            participants = config['teams']
            seeding = []
            for i in range(total_positions):
                try:
                    seeding.append({'seed_number': i+1,
                                    'team_name': participants[i]["name"],
                                    'team_id': participants[i]["id"]})
                except IndexError:
                    seeding.append({'seed_number': i+1,
                                    'team_name': None,
                                    'team_id': None})
            config["seeds"] = seeding
            matches = config['matches']
            for round in range(number_of_rounds):
                gen_matches = []
                teams_in_round = 2**(number_of_rounds - round)
                for match in range(2 ** (number_of_rounds - 1 - round)):
                    m = {'title': 'Round ' + str(round) + ' Match ' + str(match),
                         'completed': False,
                         'winner': None,
                         'winner_id': None}
                    try:
                        m['team1_id'] = config["teams"][2*match]["id"]
                        m['team1_name'] = config["teams"][2*match]["name"]
                    except IndexError:
                        m['team1_id'] = None
                        m['team1_name'] = None
                    try:
                        m['team2_id'] = config["teams"][teams_in_round-2*match-1]["id"]
                        m['team2_name'] = config["teams"][teams_in_round-2*match-1]["name"]
                    except IndexError:
                        m['team2_id'] = None
                        m['team2_name'] = None
                    gen_matches.append(m)
                matches['round' + str(round)] = gen_matches
            config = json.dumps(config, indent=4)
            with open('cargo/data/' + str(self.tour.id) + '.json', 'w+') as f:
                f.write(config)
