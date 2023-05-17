import sys
import re
import json
import urllib.request
from datetime import datetime, date, timedelta
import pprint
pp = pprint.PrettyPrinter(indent=2, compact=True)

base_dir = "/home/dmc7z/nba-stats"
get_dt = lambda x : datetime.strptime(x, "%Y-%m-%d").date()
def get_json(contents):
    m = re.search('<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', contents, re.M + re.S)
    return json.loads(m.group(1))

def get_dates(date_from, date_to):
    """ Get a list of datetimes between two given yyyy-mm-dd dates """
    begin = get_dt(date_from)
    delta = get_dt(date_to) - begin
    dates = []
    for i in range(delta.days + 1):
        day = begin + timedelta(days=i)
        dates.append(day)
    return dates

def main():
    # Get the seasons and their dates
    seasons = {}
    with open(f"{base_dir}/skeds.txt", "r") as f:
        for line in f:
            m = re.search("(\d{4}-\d{2}):(\d{4}-\d{2}-\d{2}) - (\d{4}-\d{2}-\d{2})", line)
            season, date_from, date_to = m.group(1), m.group(2), m.group(3)
            dates = get_dates(date_from, date_to)
            seasons[season] = dates

    # Loop through seasons and get daily schedules and games
    games = {}
    for season in seasons:
        print(season)
        for date in seasons[season]:
            print(f"Getting games for date={date}...")
            url =  f"https://www.nba.com/games?date={str(date)}"
            with urllib.request.urlopen(url) as u:
                contents = u.read().decode("utf-8")
                json = get_json(contents)
                _games = json["props"]["pageProps"]["games"]
                for game in _games:
                    pp.pprint(game)
                    sys.exit()
                    game[str(date)] = {
                        
                    }
"""
Getting games for date=2020-12-22...
{ 'awayTeam': { 'inBonus': None,
                'losses': 1,
                'periods': [ { 'period': 1,
                               'periodType': 'REGULAR',
                               'score': 25},
                             { 'period': 2,
                               'periodType': 'REGULAR',
                               'score': 20},
                             { 'period': 3,
                               'periodType': 'REGULAR',
                               'score': 26},
                             { 'period': 4,
                               'periodType': 'REGULAR',
                               'score': 28}],
                'score': 99,
                'seed': 0,
                'teamCity': 'Golden State',
                'teamId': 1610612744,
                'teamName': 'Warriors',
                'teamSlug': 'warriors',
                'teamTricode': 'GSW',
                'timeoutsRemaining': 1,
                'wins': 0},
  'broadcasters': { 'awayOttBroadcasters': [],
                    'awayRadioBroadcasters': [ { 'broadcastDisplay': 'KGMZ-FM',
                                                 'broadcasterId': 1597}],
                    'awayTvBroadcasters': [],
                    'homeOttBroadcasters': [],
                    'homeRadioBroadcasters': [ { 'broadcastDisplay': 'WFAN',
                                                 'broadcasterId': 1020}],
                    'homeTvBroadcasters': [],
                    'nationalBroadcasters': [ { 'broadcastDisplay': 'TNT',
                                                'broadcasterId': 10}],
                    'nationalOttBroadcasters': [],
                    'nationalRadioBroadcasters': []},
  'gameClock': '',
  'gameCode': '20201222/GSWBKN',
  'gameEt': '2020-12-22T19:00:00Z',
  'gameId': '0022000001',
  'gameLeaders': { 'awayLeaders': { 'assists': 10,
                                    'jerseyNum': '30',
                                    'name': 'Stephen Curry',
                                    'personId': 201939,
                                    'playerSlug': 'stephen-curry',
                                    'points': 20,
                                    'position': 'G',
                                    'rebounds': 4,
                                    'teamTricode': 'GSW'},
                   'homeLeaders': { 'assists': 4,
                                    'jerseyNum': '11',
                                    'name': 'Kyrie Irving',
                                    'personId': 202681,
                                    'playerSlug': 'kyrie-irving',
                                    'points': 26,
                                    'position': 'G',
                                    'rebounds': 4,
                                    'teamTricode': 'BKN'}},
  'gameStatus': 3,
  'gameStatusText': 'Final',
  'gameSubtype': '',
  'gameTimeUTC': '2020-12-23T00:00:00Z',
  'homeTeam': { 'inBonus': None,
                'losses': 0,
                'periods': [ { 'period': 1,
                               'periodType': 'REGULAR',
                               'score': 40},
                             { 'period': 2,
                               'periodType': 'REGULAR',
                               'score': 23},
                             { 'period': 3,
                               'periodType': 'REGULAR',
                               'score': 36},
                             { 'period': 4,
                               'periodType': 'REGULAR',
                               'score': 26}],
                'score': 125,
                'seed': 0,
                'teamCity': 'Brooklyn',
                'teamId': 1610612751,
                'teamName': 'Nets',
                'teamSlug': 'nets',
                'teamTricode': 'BKN',
                'timeoutsRemaining': 1,
                'wins': 1},
  'ifNecessary': False,
  'period': 4,
  'poRoundDesc': '',
  'recap': { 'entitlements': 'free',
             'excerpt': 'Kevin Durant recorded 22 points (7-16 FG), five '
                        'rebounds and three assists in his Nets debut as they '
                        'defeated the Warriors, 125-99. Kyrie Irving added 26 '
                        'points, four rebounds and four assists for the Nets '
                        'in the victory, while Stephen Curry tallied 20 '
                        'points, four rebounds and 10 assists for the Warriors '
                        'in the losing effort. Additionally for the Warriors, '
                        'James Wiseman, the No.2 overall pick in the 2020 NBA '
                        'Draft out of the University of Memphis, recorded 19 '
                        'points and six rebounds in his NBA debut. The Nets '
                        'improve to 1-0 on the season, while the Warriors fall '
                        'to 0-1.',
             'featuredImage': 'https://cdn.nba.com/manage/2020/12/1274274_landscape.jpg',
             'gameId': '0022000001',
             'id': 455178,
             'permalink': 'https://www.nba.com/watch/video/game-recap-nets-125-warriors-99-nsmxwy',
             'slug': 'game-recap-nets-125-warriors-99-2',
             'title': 'Game Recap: Nets 125, Warriors 99',
             'videoDuration': '02:15'},
  'regulationPeriods': 4,
  'seriesConference': '',
  'seriesGameNumber': '',
  'seriesText': '',
  'teamLeaders': { 'awayLeaders': { 'assists': 5.8,
                                    'jerseyNum': '30',
                                    'name': 'Stephen Curry',
                                    'personId': 201939,
                                    'playerSlug': 'stephen-curry',
                                    'points': 32,
                                    'position': 'G',
                                    'rebounds': 5.5,
                                    'teamTricode': 'GSW'},
                   'homeLeaders': { 'assists': 6,
                                    'jerseyNum': '11',
                                    'name': 'Kyrie Irving',
                                    'personId': 202681,
                                    'playerSlug': 'kyrie-irving',
                                    'points': 26.9,
                                    'position': 'G',
                                    'rebounds': 4.8,
                                    'teamTricode': 'BKN'},
                   'seasonLeadersFlag': 0}}
"""


if __name__ == "__main__":
    main()
