import sys
import re
import math
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
sys.path.append("..")
import helper

base_dir = "/home/dmc7z/nba-stats"
srs_dir = f"{base_dir}/srs"
games_dir = f"{base_dir}/data/games"

def get_srs():
    """ Get a dict of srs by team by season """
    srs = {}
    with open(f"{srs_dir}/srs.csv", "r") as f:
        for line in f:
            season, team, rating = line.strip().split(",")
            srs[season] = srs.get(season, {})
            srs[season][team] = rating
    return srs

def get_seasons():
    """ Parse the schedule and get the date bounds """
    seasons = {}
    with open(f"{base_dir}/skeds.txt", "r") as f:
        for line in f:
            m = re.search("(\d{4}-\d{2}):(\d{4}-\d{2}-\d{2}) - (\d{4}-\d{2}-\d{2})", line)
            season, date_from, date_to = m.group(1), m.group(2), m.group(3)
            seasons[season] = { "dates": { "from": date_from, "to": date_to }}
    return seasons

def get_games(srs, seasons):
    def get_season(date):
        for season in seasons:
            if date >= seasons[season]["dates"]["from"] and date <= seasons[season]["dates"]["to"]:
                return season
        raise Exception("Season not found")
    """
    Get a list of one-element lists with home-team SRS margin,
    and a list of outcomes where win=1, loss=0
    """
    # Home team SRS margin (X) and outcome (y)
    gids, X, y = [], [], []
    with open(f"{games_dir}/games.csv", "r") as f:
        for line in f:
            m = re.search("(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\s", line)
            date, gid, away, pts_a, home, pts_h = [int(m.group(i)) if i in [4,6] else m.group(i) for i in range(1,6+1)]
            if not helper.get_tricode(away, no_exc=True):
                continue
            season = get_season(date)
            # Get the SRS margin
            srs_margin = float(srs[season][home]) - float(srs[season][away])
            # Get the outcome
            outcome = int(pts_h > pts_a)
            gids.append(gid)
            X.append([srs_margin])
            y.append(outcome)
    return gids, X, y

# https://data.library.virginia.edu/logistic-regression-four-ways-with-python/
# https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
def get_model():
    srs = get_srs()
    seasons = get_seasons()
    gids, X, y = get_games(srs, seasons)

    clf = LogisticRegression(random_state=0).fit(X, y)
    return gids, { "X": X, "model": clf }

    # clf.classes_         distinct values that y takes
    # clf.intercept_       b0, e.g. array([-1.04608067])
    # clf.coef_            b1, e.g. array([[0.51491375]])
    # clf.predict_proba(x) array([[0.74002157, 0.25997843],
    #                             [0.62975524, 0.37024476],
    # clf.predict(x)       array([0, 0, 0, 1, 1, 1, 1, 1, 1, 1])
    # clf.score(X, y)

    #intercept = clf.intercept_[0]
    #coef = clf.coef_[0][0]

    """
    This...
    # p(x) = 1 / 1 + math.exp(-1 * (intercept + coef*srs_margin))
    # where math.exp(x) is "e to the power of x"
    prob = 1 / (1 + math.exp(-1 * (intercept + coef*0)))
    print(f"home_margin=0, prob={prob}")
    prob = 1 / (1 + math.exp(-1 * (intercept + coef*1)))
    print(f"home_margin=1, prob={prob}")
    prob = 1 / (1 + math.exp(-1 * (intercept + coef*2)))
    print(f"home_margin=2, prob={prob}")
    prob = 1 / (1 + math.exp(-1 * (intercept + coef*3)))
    print(f"home_margin=3, prob={prob}")
    prob = 1 / (1 + math.exp(-1 * (intercept + coef*4)))
    print(f"home_margin=4, prob={prob}")
    prob = 1 / (1 + math.exp(-1 * (intercept + coef*5)))
    print(f"home_margin=5, prob={prob}")

    ...is identical to this:
    print(clf.predict_proba([[0],[1],[2],[3],[4],[5]]))
    [[0.43555146 0.56444854]
     [0.40550412 0.59449588]
     [0.37614829 0.62385171]
     [0.34767479 0.65232521]
     [0.32025021 0.67974979]
     [0.29401387 0.70598613]]
    """

if __name__ == "__main__":
    get_model()
