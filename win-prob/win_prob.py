import sys
import re
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
    X, y = [], []
    with open(f"{games_dir}/games.csv", "r") as f:
        for line in f:
            m = re.search("(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\s", line)
            date, _, away, pts_a, home, pts_h = [int(m.group(x)) if m.group(x).isnumeric() else m.group(x) for x in range(1,6+1)]
            if not helper.get_tricode(away, no_exc=True):
                continue
            season = get_season(date)
            # Get the SRS margin
            srs_margin = float(srs[season][home]) - float(srs[season][away])
            # Get the outcome
            outcome = int(pts_h > pts_a)
            X.append([srs_margin])
            y.append(outcome)
    return X, y

def main():
    srs = get_srs()
    seasons = get_seasons()
    X, y = get_games(srs, seasons)
    print(X)
    print(y)
    import sys
    sys.exit()
    clf = LogisticRegression(random_state=0).fit(X, y)
    clf.predict(X[:2, :])
    array([0, 0])
    clf.predict_proba(X[:2, :])
    clf.score(X, y)


if __name__ == "__main__":
    main()
