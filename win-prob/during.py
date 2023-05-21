import sys
import re
import math
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
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
        gid_count = 0
        for line in f:
            # Set the gid
            m = re.search("^(\d{10})\s", line)
            if m:
                pbp = False
                gid = m.group(1) if m.group(1) in games else None
                if gid:
                    gid_count += 1
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
                if sec_rem % 720 != 0:
                    games[gid]["pbp"].append({ "margin": margin, "sec_rem": np.log(sec_rem) })
                    # Check the appropriateness of np.log re-expression
                    # https://stats.stackexchange.com/questions/298/in-linear-regression-when-is-it-appropriate-to-use-the-log-of-an-independent-va
    return games

def get_train_data(games):
    """
    X: matrix with fields margin and sec_rem
    y: list with home team outcome (win=1, loss=0)
    """
    X, y = [], []
    for i, gid in enumerate(games):
        for play in games[gid]["pbp"]:
            X.append([ play["margin"], play["sec_rem"] ])
            y.append(games[gid]["outcome"])
    return X, y

def main():
    games = get_games()
    games = get_pbp(games)

    X, y = get_train_data(games)

    poly = PolynomialFeatures(2, interaction_only=True)
    X = poly.fit_transform(X)
    clf = LogisticRegression().fit(X, y)
    intercept = clf.intercept_[0]
    coefs = clf.coef_[0]

    print(clf.classes_)
    print("up 30, at half")
    print(clf.predict_proba([[ 1, 30.0, np.log(1400), 30.0*np.log(1400)]]))
    print("up 20, at half")
    print(clf.predict_proba([[ 1, 20.0, np.log(1400), 20.0*np.log(1400)]]))
    print("up 10, at half")
    print(clf.predict_proba([[ 1, 10.0, np.log(1400), 10.0*np.log(1400)]]))
    print("up 5, at half")
    print(clf.predict_proba([[ 1, 5.0, np.log(1400), 5.0*np.log(1400)]]))
    print("tied, at half")
    print(clf.predict_proba([[ 1, 0.0, np.log(1400), 0.0*np.log(1400)]]))
    print("tied, 4 minutes left")
    print(clf.predict_proba([[ 1, 0.0, np.log(240), 0.0*np.log(240)]]))
    print("up 10, 10 minutes left")
    print(clf.predict_proba([[ 1, 10.0, np.log(600), 10.0*np.log(600)]]))
    print("up 10, 3 minutes left")
    print(clf.predict_proba([[ 1, 10.0, np.log(180), 10.0*np.log(180)]]))
    print("up 5, 3 minutes left")
    print(clf.predict_proba([[ 1, 5.0, np.log(180), 5.0*np.log(180)]]))
    print("up 10, 2 minutes left")
    print(clf.predict_proba([[ 1, 10.0, np.log(120), 10.0*np.log(120)]]))
    print("up 10, 1 minute left")
    print(clf.predict_proba([[ 1, 10.0, np.log(60), 10.0*np.log(60)]]))
    print("up 10, 10 seconds left")
    print(clf.predict_proba([[ 1, 10.0, np.log(10), 10.0*np.log(10)]]))

if __name__ == "__main__":
    main()
