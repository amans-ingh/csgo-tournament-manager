import json
import os

from cargo import db
from cargo.models import Rounds


def seeding_algorithm(start, end, teams_in_this_round, team_pos):
    if len(teams_in_this_round) > 1:
        g = int(len(teams_in_this_round) / 2)
        uh = teams_in_this_round[0:g]
        lh = teams_in_this_round[g:]
        seeding_algorithm(start, start + (end - start) / 2, uh, team_pos)
        seeding_algorithm(start + (end - start) / 2, end, lh, team_pos)
    else:
        team_pos[int(start)] = teams_in_this_round[0]
    return team_pos


class TournamentBrackets:
    def __init__(self, tournament):
        self.tour = tournament

    def single_elimination(self, round, result=None):
        if os.path.exists('cargo/data/' + str(self.tour.id) + '.json'):
            config = json.load(open('cargo/data/' + str(self.tour.id) + '.json'))
            r_num = 0
            try:
                r_num = config['basic']['total_rounds_se']
            except:
                pass
            number_of_rounds = 0
            for i in range(8):
                if self.tour.max_teams <= 2 ** i:
                    break
                number_of_rounds = number_of_rounds + 1
            config['basic']['total_rounds_se'] = number_of_rounds
            total_positions = 2 ** int(config['basic']['total_rounds_se'])
            if r_num > number_of_rounds:
                config["matches"] = {}
            if r_num != number_of_rounds:
                Rounds.query.filter_by(tour_id=self.tour.id).delete()
                for r in range(number_of_rounds):
                    round_data = Rounds(tour_id=self.tour.id,
                                        round_num=r,
                                        bo=1)
                    db.session.add(round_data)
                db.session.commit()

            # Seeding
            def ordering(b, order, r, count, n):
                if len(b) == n:
                    return order
                for u in b:
                    if order[int(u)] == -1:
                        order[int(u)] = count
                        count += 1
                        order[int(u + n / 2)] = count
                        count += 1
                r = 2 * r
                c = []
                for u in b:
                    c.append(u)
                    c.append(u + n / r)
                order = ordering(c, order, r, count, n)
                return order

            n = 2**number_of_rounds
            order = [-1] * n
            seed_numbering = ordering([0], order, 2, 0, n)
            teams = config["teams"]
            seeding = [None] * n
            t_i_r = teams
            for i, s in enumerate(seed_numbering):
                try:
                    seeding[s] = t_i_r[i]
                except IndexError:
                    break
            config["seeds"] = seeding

            # Configuring matches
            if round >= int(config['basic']['total_rounds_se']):
                round = int(config['basic']['total_rounds_se']) - 1
            try:
                matches = config['matches']
            except KeyError:
                config['matches'] = {}
                matches = config['matches']

            # Assigning matches
            if round == 0:
                try:
                    matchData = config["matches"]["round0"]
                    # Update other matches
                    for match in range(2 ** (number_of_rounds - 1 - round)):
                        m = matchData[str(match)]
                        m['title'] = 'Round ' + str(round) + ' Match ' + str(match)
                        m['team1'] = seeding[2 * match]
                        m['team2'] = seeding[2 * match + 1]
                    if result:
                        match = matchData[str(result["match"])]
                        winnerId = result["winnerId"]
                        winner = None
                        try:
                            if match["team1"]:
                                if match["team1"]["id"] == winnerId:
                                    winner = match["team1"]
                        except KeyError:
                            pass
                        try:
                            if match["team2"]:
                                if match["team2"]["id"] == winnerId:
                                    winner = match["team2"]
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
                            if match["team1"]:
                                if match["team1"]["id"] == winnerId:
                                    winner = match["team1"]
                        except KeyError:
                            pass
                        try:
                            if match["team2"]:
                                if match["team2"]["id"] == winnerId:
                                    winner = match["team2"]
                        except KeyError:
                            pass
                        if winner:
                            match["winner"] = winner
                matches['round' + str(round)] = matchData

            else:
                try:
                    matchData = config["matches"]["round" + str(round)]
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
                        m['team1'] = team1
                        m['team2'] = team2
                    if result:
                        match = matchData[str(result["match"])]
                        winnerId = result["winnerId"]
                        winner = None
                        try:
                            if match["team1"]["id"] == winnerId:
                                winner = match["team1"]
                        except KeyError:
                            pass
                        try:
                            if match["team2"]["id"] == winnerId:
                                winner = match["team2"]
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
