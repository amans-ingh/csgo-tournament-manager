import json
import os


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
                    print(number_of_rounds)
                    if self.tour.max_teams <= 2 ** i:
                        break
                    number_of_rounds = number_of_rounds + 1
                config['basic']['total_rounds_se'] = number_of_rounds
            matches = config['matches']
            for round in range(number_of_rounds):
                gen_matches = []
                for match in range(2 ** (number_of_rounds - 1 - round)):
                    m = {'title': 'Round ' + str(round) + ' Match ' + str(match)}
                    gen_matches.append(m)
                matches['round' + str(round)] = gen_matches
            config = json.dumps(config, indent=4)
            with open('cargo/data/' + str(self.tour.id) + '.json', 'w+') as f:
                f.write(config)
