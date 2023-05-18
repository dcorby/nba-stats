import sys
import re
import json
import urllib.request
import glob
import pprint
pp = pprint.PrettyPrinter(indent=2, compact=True)
from termcolor import colored, cprint

""" Get the games from /data/games/ and download and parse the box scores """

base_dir = "/home/dmc7z/nba-stats"
def get_json(contents):
    m = re.search('<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', contents, re.M + re.S)
    return json.loads(m.group(1))

def main():
    files = glob.glob(f"{base_dir}/data/games/*.csv")
    for _file in sorted(files):
        date = _file.replace(".csv", "").split("/")[-1]
        cprint(f"Processing games file for date={date}", "cyan")
        ids = []
        with open(_file, "r") as f:
            for line in f:
                id = line.split(",")[1]
                ids.append(id)
        for id in ids:
            url = f"https://www.nba.com/game/foo-vs-bar-{id}/box-score#box-score"
            cprint(f"Downloading box score for date={date}, game={id}", "cyan")
            with urllib.request.urlopen(url) as u:
                contents = u.read().decode("utf-8")
                json = get_json(contents)
                #pp.pprint(json)
                
                sys.exit()
            
            
        sys.exit()
    

"""
props pageProps game awayTeam players[] firstName|familyName|position|personId|statistics 

                                                                   'statistics': { 'assists': 1,
                                                                                   'blocks': 1,
                                                                                   'fieldGoalsAttempted': 16,
                                                                                   'fieldGoalsMade': 4,
                                                                                   'fieldGoalsPercentage': 0.25,
                                                                                   'foulsPersonal': 4,
                                                                                   'freeThrowsAttempted': 4,
                                                                                   'freeThrowsMade': 3,
                                                                                   'freeThrowsPercentage': 0.75,
                                                                                   'minutes': '31:14',
                                                                                   'plusMinusPoints': -28,
                                                                                   'points': 13,
                                                                                   'reboundsDefensive': 2,
                                                                                   'reboundsOffensive': 0,
                                                                                   'reboundsTotal': 2,
                                                                                   'steals': 0,
                                                                                   'threePointersAttempted': 6,
                                                                                   'threePointersMade': 2,
                                                                                   'threePointersPercentage': 0.333,
                                                                                   'turnovers': 4}},
"""



if __name__ == "__main__":
    main()
