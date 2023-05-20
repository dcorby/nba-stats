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

def main():

    # Get skeds
    seasons = {}
    with open(f"{base_dir}/skeds.txt", "r") as f:
        for line in f:
            m = re.search("(\d{4}-\d{2}):(\d{4}-\d{2}-\d{2}) - (\d{4}-\d{2}-\d{2})", line)
            season, date_from, date_to = m.group(1), m.group(2), m.group(3)
            seasons[season] = { "dates": { "from": date_from, "to": date_to }}

    def get_season(date):
        for season in seasons:
            if date >= seasons[season]["dates"]["from"] and seasons[season]["dates"]["to"]:
                return season
        raise Exception("Season not found")

    with open(f"{games_dir}/games.csv", "r") as f:
        for line in f:
            # e.g. 2023-04-09,0022201230,warriors,157,blazers,101
            m = re.search("(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\s", line)
            date, gid, away, pts_a, home, pts_h = [int(m.group(x)) if m.group(x).isnumeric() else m.group(x) for x in range(1,6+1)]
            season = get_season(date)

            # Make sure it's a real game
            if not helper.get_tricode(away):
                continue

            # Seasons has a teams property, holding raw data for calculation
            teams = seasons.get("teams", {})
            mov_a = pts_a - pts_h
            mov_h = pts_h - pts_a
            teams[away] = teams.get(away, { "vs": [], "mov": [], "avg_mov": None })
            teams[home] = teams.get(home, { "vs": [], "mov": [], "avg_mov": None })
            teams[away]["vs"].append(away)
            teams[home]["vs"].append(home)
            teams[away]["mov"].append(mov_a)
            teams[home]["mov"].append(mov_h)

            for team in teams:
                teams[team]["avg_mov"] = statistics.fmean(teams[team]["mov"])

            coeffs = []     # left hand side
            constants = []  # right hand side

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
            dct = {}
            for i, team in enumerate(teams):
                dct[team] = srs[i]
            print(season)
            pp.pprint(dct)


if __name__ == "__main__":
    main()
