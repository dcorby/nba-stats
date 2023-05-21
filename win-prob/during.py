import sys
import re
import math
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
sys.path.append("..")
import helper

base_dir = "/home/dmc7z/nba-stats"
games_dir = f"{base_dir}/data/games"
game_dir = f"{base_dir}/data/game"

def get_games():
    """ 
    Get the game data, incl. gid, home team, and outcome 
    games = { <gid>: { "home": <home>, "outcome": <outcome>, ...}...}
    """
    games = {}
    with open(f"{games_dir}/games.csv", "r") as f:
        for line in f:
            m = re.search("(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\s", line)
            _, gid, __, pts_a, home, pts_h = [int(m.group(x)) if x in [4,6] else m.group(x) for x in range(1,6+1)]
            if not helper.get_tricode(home, no_exc=True):
                continue
            games[gid] = { "home": home, "outcome": int(pts_h > pts_a), "pbp": [] }
    return games

def get_pbp(games):
    """ 
    Parse game.csv and add pbp to the games dict, for the associated game 
    Only need (1) seconds remaining until end of 4th, (2) home margin
    """
    with open(f"{game_dir}/game.csv", "r") as f:
        gid = None
        pbp = False
        for line in f:
            # Set the gid
            m = re.search("^(\d{10})\s", line)
            if m:
                pbp = False
                gid = m.group(1) if m.group(1) in games else None
            # If a game is set activate pbp
            if gid and line.strip() == "pbp":
                pbp = True
                continue
            # If pbp is active, add it to the associated game
            if pbp:
                tokens = line.split(",")
                if tokens[10] == "":
                    continue
                clock, period, margin = tokens[0], int(tokens[1]), int(tokens[10]) - int(tokens[11])
                clock = clock.replace("PT", "").split(".")[0]
                minutes, seconds = [int(x) for x in clock.split("M")]
                sec_rem = 4*12*60 - (12*60*(period-1)) - (12*60 - (minutes*60 + seconds))
                games[gid].append({ "sec_rem": sec_rem, "margin": margin })

def main():
    games = get_games()
    games = get_pbp(games)

if __name__ == "__main__":
    main()
