import sys
import re
import json
import time
import urllib.request
import glob
from pathlib import Path
import pprint
pp = pprint.PrettyPrinter(indent=2, compact=True)
from termcolor import colored, cprint

""" 
Get the games from /data/games/ and download and parse the box scores
Write to files by game, then combine them to two files, box.csv and players.csv
"""

base_dir = "/home/dmc7z/nba-stats"
box_dir = f"{base_dir}/data/box"
games_dir = f"{base_dir}/data/games"

def get_json(contents):
    m = re.search('<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', contents, re.M + re.S)
    return json.loads(m.group(1))

def main():

    # Confirm to overwrite box.csv if it exists
    if Path(f"{box_dir}/box.csv").is_file() or Path(f"{box_dir}/players.csv").is_file():
        ans = input("Continue and overwrite box.csv and players.csv? ")
        if ans != "y":
            sys.exit()

    games = []
    with open(f"{games_dir}/games.csv", "r") as f:
        for line in f:
            date, id = line.split(",")[0], line.split(",")[1]
            games.append((date, id))
    players = {}
    for game in games:
        date, id = game
        url = f"https://www.nba.com/game/foo-vs-bar-{id}/box-score#box-score"
        pathname = f"{box_dir}/{id}.csv"
        cprint(f"Getting box score for date={date}, game={id}", "cyan")
        if Path(pathname).is_file():
            cprint(f"File for date={date}, id={id} already exists, skipping", "yellow")
            continue
        # Add the id
        lines = [id]
        with urllib.request.urlopen(url) as u:
            contents = u.read().decode("utf-8")
            json = get_json(contents)
            for team in ["away", "home"]:
                # Add the team
                lines.append(team)
                for player in json["props"]["pageProps"]["game"][f"{team}Team"]["players"]:
                    # Get the player info
                    stats = []
                    stats.append(player["personId"])
                    name = player["firstName"] + " " + player["familyName"]
                    stats.append(player["position"])
                    # Get the stats
                    s = player["statistics"]
                    stats.append(s["assists"])
                    stats.append(s["blocks"])
                    stats.append(s["fieldGoalsAttempted"])
                    stats.append(s["fieldGoalsMade"])
                    stats.append(s["foulsPersonal"])
                    stats.append(s["freeThrowsAttempted"])
                    stats.append(s["freeThrowsMade"])
                    stats.append(s["minutes"])
                    stats.append(s["plusMinusPoints"])
                    stats.append(s["points"])
                    stats.append(s["reboundsDefensive"])
                    stats.append(s["reboundsOffensive"])
                    stats.append(s["reboundsTotal"])
                    stats.append(s["steals"])
                    stats.append(s["threePointersAttempted"])
                    stats.append(s["threePointersMade"])
                    stats.append(s["turnovers"])
                    # Add the stats
                    lines.append(",".join([str(x) for x in stats]))
            with open(pathname, "w") as f:
                for line in lines:
                    f.write(f"{line}\n")
            time.sleep(1)


if __name__ == "__main__":
    main()
