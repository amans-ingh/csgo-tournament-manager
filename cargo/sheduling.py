import datetime
import json
import os

from cargo import scheduler
from cargo.functions import participant_map_veto, tour_enable, tour_disable
from cargo.models import Tournament


def cron_params(date, time):
    date = date.split("-")
    time = time.split(":")
    year = date[0]
    month = date[1]
    day = date[2]
    hour = time[0]
    minute = time[1]
    return year, month, day, hour, minute


def schedule_match_events(tour_id, round_num, match_num):
    if os.path.exists('cargo/data/' + str(tour_id) + '.json'):
        config = json.load(open('cargo/data/' + str(tour_id) + '.json'))
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
    year, month, day, hour, minute = cron_params(match["date"], match["time"])
    tour = Tournament.query.get(tour_id)
    r_n = round_num.split("round")
    r_n = int(r_n[1])
    matchid = 2048*(int(tour.id)+1) + 256*(r_n + 1) + (int(match_num)+1)
    if tour:
        scheduler.add_job(trigger='cron', func=participant_map_veto, args=[tour, round_num, match_num],
                          id=str(matchid)+'ma',
                          year=year, month=month, day=day,
                          hour=hour, minute=minute)


def unschedule_match_events(tour_id, round_num, match_num):
    tour = Tournament.query.get(tour_id)
    r_n = round_num.split("round")
    r_n = int(r_n[1])
    matchid = 2048*(int(tour.id)+1) + 256*(r_n + 1) + (int(match_num)+1)
    if tour:
        try:
            scheduler.remove_job(str(matchid)+'ma')
        except:
            pass


def schedule_tour_events(tour):
    year, month, day, hour, minute = cron_params(tour.reg_start, tour.reg_start_time)
    reg_open = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    if reg_open > datetime.datetime.now():
        scheduler.add_job(trigger='cron', func=tour_enable, args=[tour],
                          id=str(tour.id)+'te',
                          year=year, month=month, day=day,
                          hour=hour, minute=minute)
    else:
        tour_enable(tour)

    year, month, day, hour, minute = cron_params(tour.reg_end, tour.reg_end_time)
    reg_close = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    if reg_close < datetime.datetime.now():
        tour_disable(tour)
    else:
        scheduler.add_job(trigger='cron', func=tour_disable, args=[tour],
                          id=str(tour.id)+'ts',
                          year=year, month=month, day=day,
                          hour=hour, minute=minute)


def unschedule_tour_events(tour):
    try:
        scheduler.remove_job(str(tour.id)+'te')
    except:
        pass
    try:
        scheduler.remove_job(str(tour.id)+'ts')
    except:
        pass
