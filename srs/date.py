import sys
import re
import numpy as np
import statistics
import pprint
pp = pprint.PrettyPrinter(indent=2, compact=True)
sys.path.append("..")
import helper

base_dir = "/home/dmc7z/nba-stats"
games_dir = f"{base_dir}/data/games"
srs_dir = f"{base_dir}/srs"

def get_srs(seasons, for_season, thru_date):
    """ Collect the raw data games.csv """
    def get_season(date):
        for season in seasons:
            if date >= seasons[season]["dates"]["from"] and date <= seasons[season]["dates"]["to"]:
                return season
        raise Exception("Season not found")
    teams = {}
    with open(f"{games_dir}/games.csv", "r") as f:
        for line in f:
            # e.g. 2023-04-09,0022201230,warriors,157,blazers,101
            m = re.search("(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\s", line)
            date, gid, away, pts_a, home, pts_h = [int(m.group(x)) if m.group(x).isnumeric() else m.group(x) for x in range(1,6+1)]
            season = get_season(date)

            # Make sure it's a real game
            if not helper.get_tricode(away, no_exc=True):
                continue

            mov_a = pts_a - pts_h
            mov_h = pts_h - pts_a
            teams[away] = teams.get(away, { "vs": [], "mov": [], "avg_mov": None })
            teams[home] = teams.get(home, { "vs": [], "mov": [], "avg_mov": None })
            teams[away]["vs"].append(home)
            teams[home]["vs"].append(away)
            teams[away]["mov"].append(mov_a)
            teams[home]["mov"].append(mov_h)
            for team in teams:
                teams[team]["avg_mov"] = statistics.fmean(teams[team]["mov"])
            # Update teams property
            seasons[season]["teams"] = teams

    """ Compute SRS for seasons """
    coeffs = []     # left hand side
    constants = []  # right hand side
    teams = seasons[season]["teams"]
    for team in teams:
        cfs = []
        for opp in teams:
            if team == opp:
                cfs.append(-1)
            elif team in teams.keys():
                cfs.append(1 / len(teams[team]["vs"]))
            else:
                cfs.append(0)
        coeffs.append(cfs)
        constants.append(teams[team]["avg_mov"] * -1)

    srs = np.linalg.solve(np.array(coeffs), np.array(constants)).tolist()
    for i, team in enumerate(teams):
        teams[team]["srs"] = srs[i]
        del teams[team]["vs"]
        del teams[team]["mov"]
        del teams[team]["avg_mov"]
    return teams

def main():
    """ Parse the schedule and get the date bounds """
    seasons = {}
    for season in ["2020-21", "2021-22", "2022-23"]:
        with open(f"{base_dir}/skeds.txt", "r") as f:
            for line in f:
                m = re.search("(\d{4}-\d{2}):(\d{4}-\d{2}-\d{2}) - (\d{4}-\d{2}-\d{2})", line)
                season, date_from, date_to = m.group(1), m.group(2), m.group(3)
                seasons[season] = { "dates": { "from": date_from, "to": date_to }}
    data = {}
    for season in seasons:
        for date in helper.get_dates(seasons[season]["dates"]["from"], seasons[season]["dates"]["to"]):
            print(f"SRS for season={season}, thru date={date}...")
            teams = get_srs(seasons, season, date)
            data[season] = data.get(season, { "dates": [], "teams": {} })
            data[season]["dates"].append(date)
            for team in teams:
                data[season]["teams"][team] = data[season]["teams"].get(team, [])
                data[season]["teams"][team].append(teams[team]["srs"])

if __name__ == "__main__":
    main()

