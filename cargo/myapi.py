import json
import os

from flask_restful import Resource
from cargo import application


class GenerateConfig:
    def __init__(self, tour_id, round_num, match_num):
        self.tour_id = tour_id
        self.round_num = round_num
        self.match_num = match_num

    def find_maps(self):
        if os.path.exists('cargo/data/' + str(self.tour_id) + '.json'):
            config = json.load(open('cargo/data/' + str(self.tour_id) + '.json'))
            maps_to_play = []
            maps_to_be_played = []
            try:
                maplist = config["matches"]["round"+str(self.round_num)][str(self.match_num)]["vetostatus"]["mapstatus"]
                for map in maplist:
                    if maplist[map]:
                        maps_to_be_played.append(map)
            except KeyError:
                return ['de_mirage']
            for maps in maps_to_be_played:
                maps_to_play.append('de_' + maps)
            return maps_to_play
        return ['de_mirage']

    def find_teams(self):
        team_a = None
        team_b = None
        match_id = None
        if os.path.exists('cargo/data/' + str(self.tour_id) + '.json'):
            config = json.load(open('cargo/data/' + str(self.tour_id) + '.json'))
            try:
                team_a = config["matches"]["round"+str(self.round_num)][str(self.match_num)]["team1"]
                team_b = config["matches"]["round" + str(self.round_num)][str(self.match_num)]["team2"]
                team_a['flag'] = 'FR'
                team_a['logo'] = 'nipta'
                team_b['flag'] = 'SE'
                team_b['logo'] = 'niptb'
                match_id = 2048*(self.tour_id+1) + 256*(self.round_num+1) + (self.match_num+1)
            except KeyError:
                team_a = None
                team_b = None
        return team_a, team_b, match_id


class MyApiMatchStart(Resource):
    def get(self, tour_id, round_num, match_num, event):
        if event == 'config':
            config_generator = GenerateConfig(tour_id, round_num, match_num)
            team_a, team_b, match_id = config_generator.find_teams()
            config = {'matchid': match_id,
                      'num_maps': len(config_generator.find_maps()),
                      'skip_veto': True,
                      'side_type': 'always_knife',
                      'maplist': config_generator.find_maps(),
                      'players_per_team': 5,
                      'min_players_to_ready': 1,
                      'min_spectators_to_ready': 0,
                      'team1': team_a,
                      'team2': team_b,
                      'cvars': {'get5_web_api_key': application.config['SERVER_URL'],
                                'get5_web_api_url': application.config['SERVER_URL'],
                                'hostname': 'Match is live'
                                }
                      }
            return config
        return {'message': 'Invalid request'}
