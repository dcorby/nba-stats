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
import helper
import shutil

""" 
Get the games from /data/games/ and download and parse the box scores
Write to files by game, then combine them to two files, box.csv and players.csv
"""

base_dir = "/home/dmc7z/nba-stats"
games_dir = f"{base_dir}/data/games"
game_dir = f"{base_dir}/data/game"

def get_json(contents):
    m = re.search('<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', contents, re.M + re.S)
    return json.loads(m.group(1))

def main():
    # Confirm to overwrite box|pbp|players.csv if any exist
    if any([Path(f"{game_dir}/{x}.csv").is_file() for x in ["box","pbp","players"]]):
        ans = input("Continue and overwrite box|pbp|players.csv? ")
        if ans != "y":
            sys.exit()

    games = []
    with open(f"{games_dir}/games.csv", "r") as f:
        for line in f:
            tokens = line.split(",")
            date, id, away, home = tokens[0], tokens[1], tokens[2], tokens[4]
            games.append({ "date": date, "id": id, "away": away, "home": home })
    players = {}
    for game in games:
        if game["id"] in helper.special_games:
            continue
        url = f"https://www.nba.com/game/foo-vs-bar-{game['id']}/box-score#box-score"
        pathname = f"{game_dir}/{game['id']}.csv"
        cprint(f"Getting box score for date={game['date']}, game={game['id']}", "cyan")
        if Path(pathname).is_file():
            cprint(f"File for date={game['date']}, id={game['id']} already exists, skipping", "yellow")
            continue
        # Add the id
        lines = [game["id"]]
        with urllib.request.urlopen(url) as u:
            contents = u.read().decode("utf-8")
            json = get_json(contents)
            for team in ["away", "home"]:
                # Add the team
                lines.append(f"{team},{game[team]}")
                for player in json["props"]["pageProps"]["game"][f"{team}Team"]["players"]:
                    # Get the player info
                    stats = []
                    stats.append(player["personId"])
                    stats.append(player["firstName"])
                    stats.append(player["familyName"])
                    stats.append(player["nameI"])
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

            lines.append("pbp")
            plays = []
            for action in json["props"]["pageProps"]["playByPlay"]["actions"]:
                play = []
                for token in helper.action:
                    play.append(action[token])
                plays.append(play)
            for play in plays:
                lines.append(",".join([str(x) for x in play]))

            with open(pathname, "w") as f:
                for line in lines:
                    f.write(f"{line}\n")
            time.sleep(0.25)

    # Concat all the files and delete the game files
    outpathname = f"{game_dir}/game.csv"
    with open(outpathname, "w") as outfile:
        for pathname in sorted(glob.glob(f"{game_dir}/*.csv")):
            id = pathname.replace(".csv", "").split("/")[-1]
            if id in helper.special_games:
                continue
            if pathname == outpathname:
                continue
            with open(pathname, "r") as infile:
                shutil.copyfileobj(infile, outfile)
        for pathname in glob.glob(f"{game_dir}/*.csv"):
            if pathname != outpathname:
                Path(pathname).unlink()
                
if __name__ == "__main__":
    main()
