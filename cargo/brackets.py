import json
import os
from cargo.models import Registration


class TournamentBrackets:
    def __init__(self, tournament):
        self.tour = tournament

    def single_elimination(self, round, result=None):
        if os.path.exists('cargo/data/' + str(self.tour.id) + '.json'):
            config = json.load(open('cargo/data/' + str(self.tour.id) + '.json'))
            try:
                number_of_rounds = config['basic']['total_rounds_se']
            except KeyError:
                number_of_rounds = 0
                for i in range(8):
                    if self.tour.max_teams <= 2 ** i:
                        break
                    number_of_rounds = number_of_rounds + 1
                config['basic']['total_rounds_se'] = number_of_rounds
            total_positions = 2 ** int(config['basic']['total_rounds_se'])

            # Alternate seeding
            seeding = [None] * total_positions
            teams = config["teams"]
            for n in range(int(2 ** (number_of_rounds - 1))):
                try:
                    seeding[2 * n] = teams[n]
                except IndexError:
                    seeding[2 * n] = None
            for n in range(int(2 ** (number_of_rounds - 1))):
                try:
                    seeding[2 * n + 1] = teams[n + int(2 ** (number_of_rounds - 1))]
                except IndexError:
                    seeding[2 * n + 1] = None
            config["seeds"] = seeding

            # Configuring matches
            if round >= int(config['basic']['total_rounds_se']):
                round = int(config['basic']['total_rounds_se']) - 1
            try:
                matches = config['matches']
            except KeyError:
                config['matches'] = {}
                matches = config['matches']
            if round == 0:
                try:
                    matchData = config["matches"]["round0"]
                    # Update other matches
                    for match in range(2 ** (number_of_rounds - 1 - round)):
                        m = matchData[str(match)]
                        m['title'] = 'Round ' + str(round) + ' Match ' + str(match)
                        m['team1'] = seeding[2 * match],
                        m['team2'] = seeding[2 * match + 1]
                    if result:
                        match = matchData[result["match"]]
                        winnerId = result["winnerId"]
                        winner = None
                        try:
                            if match["team1"]["id"] == winnerId:
                                winner = match["team1"]
                        except KeyError:
                            pass
                        try:
                            if match["team1"]["id"] == winnerId:
                                winner = match["team1"]
                        except KeyError:
                            pass
                        if winner:
                            match["winner"] = winner

                except KeyError:
                    gen_matches = []
                    for match in range(2 ** (number_of_rounds - 1 - round)):
                        m = {'title': 'Round ' + str(round) + ' Match ' + str(match),
                             'team1': seeding[2 * match],
                             'team2': seeding[2 * match + 1]}
                        gen_matches.append(m)
                    matchData = {}
                    for i, mat in enumerate(gen_matches):
                        matchData[i] = mat
                    if result:
                        match = matchData[result["match"]]
                        winnerId = result["winnerId"]
                        winner = None
                        try:
                            if match["team1"]["id"] == winnerId:
                                winner = match["team1"]
                        except KeyError:
                            pass
                        try:
                            if match["team1"]["id"] == winnerId:
                                winner = match["team1"]
                        except KeyError:
                            pass
                        if winner:
                            match["winner"] = winner
                matches['round' + str(round)] = matchData



            if round:
                try:
                    matchData = config["matches"]["round"+str(round)]
                    # Update other matches
                    for match in range(2 ** (number_of_rounds - 1 - round)):
                        m = matchData[str(match)]
                        try:
                            team1 = config["matches"]["round" + str(round - 1)][str(2 * match)]["winner"]
                        except KeyError:
                            team1 = None
                        try:
                            team2 = config["matches"]["round" + str(round - 1)][str(2 * match + 1)]["winner"]
                        except:
                            team2 = None
                        m['title'] = 'Round ' + str(round) + ' Match ' + str(match)
                        m['team1'] = team1,
                        m['team2'] = team2
                    if result:
                        match = matchData[result["match"]]
                        winnerId = result["winnerId"]
                        winner = None
                        try:
                            if match["team1"]["id"] == winnerId:
                                winner = match["team1"]
                        except KeyError:
                            pass
                        try:
                            if match["team1"]["id"] == winnerId:
                                winner = match["team1"]
                        except KeyError:
                            pass
                        if winner:
                            match["winner"] = winner
                except KeyError:
                    gen_matches = []
                    for match in range(2 ** (number_of_rounds - 1 - round)):
                        try:
                            team1 = config["matches"]["round" + str(round - 1)][str(2 * match)]["winner"]
                        except KeyError:
                            team1 = None
                        try:
                            team2 = config["matches"]["round" + str(round - 1)][str(2 * match + 1)]["winner"]
                        except:
                            team2 = None
                        m = {'title': 'Round ' + str(round) + ' Match ' + str(match), 'completed': False,
                             'team1': team1,
                             'team2': team2}
                        gen_matches.append(m)
                    matchData = {}
                    for i, mat in enumerate(gen_matches):
                        matchData[i] = mat
                matches['round' + str(round)] = matchData
            config = json.dumps(config, indent=4)
            with open('cargo/data/' + str(self.tour.id) + '.json', 'w+') as f:
                f.write(config)
