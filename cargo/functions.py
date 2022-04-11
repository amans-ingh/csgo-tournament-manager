import json
import os


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
                                'seed': 0,
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
            if team['id'] == reg_team.id:
                config['teams'].remove(team)
                con = json.dumps(config, indent=4)
                with open('cargo/data/' + str(tour.id) + '.json', 'w+') as f:
                    f.write(con)
                return True
            return False
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
                reg_team.p1 = nicknames[0]
                reg_team.p2 = nicknames[1]
                reg_team.p3 = nicknames[2]
                reg_team.p4 = nicknames[3]
                reg_team.p5 = nicknames[4]
                reg_team.p1_steam_id = steam_id[0]
                reg_team.p2_steam_id = steam_id[1]
                reg_team.p3_steam_id = steam_id[2]
                reg_team.p4_steam_id = steam_id[3]
                reg_team.p5_steam_id = steam_id[4]
                return reg_team
            return False
        return False
    return False
