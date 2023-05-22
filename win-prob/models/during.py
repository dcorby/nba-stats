import sys
import re
import math
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import numpy as np
import pprint
pp = pprint.PrettyPrinter(indent=2, compact=True)
sys.path.append("..")
import helper

"""
This person has the same solution, namely to model time frames separately
to circumvent non-linearity of time remaining to win prob relationship
https://sports.sites.yale.edu/ncaa-basketball-win-probability-model
"""

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
            date, gid, away, pts_a, home, pts_h = [int(m.group(x)) if x in [4,6] else m.group(x) for x in range(1,6+1)]
            if not helper.get_tricode(home, no_exc=True):
                continue
            games[gid] = { "date": date, "home": home, "away": away, "outcome": int(pts_h > pts_a), "pbp": [] }
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
                # Just train it on regulation
                if period > 4:
                    continue
                clock = clock.replace("PT", "").split(".")[0]
                minutes, seconds = [int(x) for x in clock.split("M")]
                sec_rem = 4*12*60 - (12*60*(period-1)) - (12*60 - (minutes*60 + seconds))
                # Backfill
                if len(games[gid]["pbp"]) > 0:
                    prev = games[gid]["pbp"][-1]
                    diff = prev["sec_rem"] - sec_rem
                    if diff > 1:
                        for add, i in enumerate(range(0, diff)):
                            games[gid]["pbp"].append({ "margin": prev["margin"], "sec_rem": prev["sec_rem"] - add })
                games[gid]["pbp"].append({ "margin": margin, "sec_rem": sec_rem })
                    
    return games

def get_train_data(games):
    """
    X: matrix with fields margin and sec_rem
    y: list with home team outcome (win=1, loss=0)
    """
    gids, X, y = [], {}, {}
    for i, gid in enumerate(games):
        for play in games[gid]["pbp"]:
            if play["sec_rem"] == 0:
                continue
            sec_rem = play["sec_rem"]
            X[sec_rem] = X.get(sec_rem, [])
            y[sec_rem] = y.get(sec_rem, [])
            X[sec_rem].append([ play["margin"], sec_rem ])
            y[sec_rem].append(games[gid]["outcome"])
        gids.append(gid)
    return gids, X, y

def get_models():
    games = get_games()
    games = get_pbp(games)

    gids, X, y = get_train_data(games)

    models = {}
    for sec_rem in sorted(X.keys()):
        _X = X[sec_rem]
        _y = y[sec_rem]

        poly = preprocessing.PolynomialFeatures(2, interaction_only=True)
        _X = poly.fit_transform(_X)

        clf = LogisticRegression(class_weight={0:0.55,1:0.45}).fit(_X, _y)
        clf = LogisticRegression().fit(_X, _y)
        models[sec_rem] = { "X": _X, "model": clf }
        #intercept = clf.intercept_[0]
        #coefs = clf.coef_[0]
        #print(f"up 10, {sec_rem} sec left")
        #print(clf.predict_proba([[ 1, 10.0, sec_rem, 10.0*sec_rem]]))
    return games, models

if __name__ == "__main__":
    get_models()
