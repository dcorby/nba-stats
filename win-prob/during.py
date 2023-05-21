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
                #if sec_rem <= 5:
                #    print(period, sec_rem)
                if sec_rem % 720 != 0:
                    #games[gid]["pbp"].append({ "margin": margin, "sec_rem": sec_rem })
                    games[gid]["pbp"].append({ "margin": margin, "sec_rem": np.log(sec_rem) })
            #if gid_count > 5:
            #    sys.exit()
    return games

def get_train_data(games):
    """
    X: matrix with fields margin and sec_rem
    y: list with home team outcome (win=1, loss=0)
    """
    X, y = [], []
    for i, gid in enumerate(games):
        for play in games[gid]["pbp"]:
            #X.append([ play["margin"], play["sec_rem"], play["margin"]*play["sec_rem"] ])
            X.append([ play["margin"], play["sec_rem"] ])
            #X.append([ play["pred"] ])
            y.append(games[gid]["outcome"])

            #X.append([ -1*play["margin"], play["sec_rem"] ])
            #y.append(int(not bool(games[gid]["outcome"])))

            #if play["sec_rem"] <= 5:
            #    print(play)
        #if i == 5:
        #    print("5 games finished...")
        #    sys.exit()

    return X, y

def main():
    games = get_games()
    games = get_pbp(games)

    X, y = get_train_data(games)

    poly = PolynomialFeatures(2, interaction_only=True)
    X = poly.fit_transform(X)

    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

    #for i, row in enumerate(X):
    #    if -3 <= row[0] <= -1 and row[1] < 30:
    #        print(row, y[i])

    #def log_transform(x):
    #    print(x)
    #    return np.log(x + 1)

    #from sklearn.preprocessing import StandardScaler
    #from sklearn.pipeline import Pipeline
    #scaler = StandardScaler()
    #transformer = FunctionTransformer(log_transform)
    #pipe = Pipeline([('scaler', scaler), ('transformer', transformer), ('regressor', LogisticRegression())])
    #pipe.fit(X, y)

    clf = LogisticRegression().fit(X, y)
    #clf = LogisticRegression().fit(X, y)
    #clf = LogisticRegression(random_state=0).fit(X_train, y_train)
    intercept = clf.intercept_[0]
    coefs = clf.coef_[0]

    #print(intercept)
    #print(coefs)

    # Make some predictions
    # https://scikit-learn.org/stable/modules/preprocessing.html#polynomial-features
    # PolynomialFeatures(2) -> 1,X1,X2,X1^2,X1*X2,X2^2
    #print(clf.predict_proba([[1, -10, 5, -10*-10, -10*5, 5*5]]))
    #print(clf.predict_proba([[1, -10, 5, -10*5]]))
    #print(clf.predict_proba([[-10, 5]]))
    #print(clf.predict_proba([[np.log(-10/5)]]))
    print(clf.classes_)
    #print(clf.predict_proba([[ 10.0 + (1400/2800)*6.86, 1400]]))
    print(clf.predict_proba([[ 1, 10.0, np.log(10), 10.0*np.log(10)]]))
    print(clf.predict_proba([[ 1, 10.0, np.log(1400), 10.0*np.log(1400)]]))


if __name__ == "__main__":
    main()
