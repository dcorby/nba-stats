import sys
import re
import json
import shutil
import glob
import urllib.request
from datetime import datetime, date, timedelta
import pprint
pp = pprint.PrettyPrinter(indent=2, compact=True)
from termcolor import colored, cprint
from pathlib import Path
import time

"""
Parse skeds.txt and get the game summaries for all seasons and dates
Write to files by date then concat to games.csv
"""

base_dir = "/home/dmc7z/nba-stats"
games_dir = f"{base_dir}/data/games"

get_dt = lambda x : datetime.strptime(x, "%Y-%m-%d").date()
def get_json(contents):
    m = re.search('<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', contents, re.M + re.S)
    return json.loads(m.group(1))

def get_dates(date_from, date_to):
    """ Get a list of datetimes between two given yyyy-mm-dd dates """
    begin = get_dt(date_from)
    delta = get_dt(date_to) - begin
    dates = []
    for i in range(delta.days + 1):
        day = begin + timedelta(days=i)
        dates.append(day)
    return dates

def main():

    # Confirm to overwrite games.csv if it exists
    if Path(f"{games_dir}/games.csv").is_file():
        ans = input("Continue and overwrite games.csv? ")
        if ans != "y":
            sys.exit()

    # Get the seasons and their dates
    seasons = {}
    with open(f"{base_dir}/skeds.txt", "r") as f:
        for line in f:
            m = re.search("(\d{4}-\d{2}):(\d{4}-\d{2}-\d{2}) - (\d{4}-\d{2}-\d{2})", line)
            season, date_from, date_to = m.group(1), m.group(2), m.group(3)
            dates = get_dates(date_from, date_to)
            seasons[season] = dates

    # Loop through seasons and get daily schedules and games
    for season in seasons:
        cprint(f"Getting games for season={season}", "cyan", attrs=["bold"])
        for date in seasons[season]:
            pathname = f"{games_dir}/{str(date)}.csv"
            cprint(f"Getting games for season={season}, date={date}", "cyan")
            if Path(pathname).is_file():
                cprint(f"File for date={date} already exists, skipping", "yellow")
                continue
            url = f"https://www.nba.com/games?date={str(date)}"
            lines = []
            with urllib.request.urlopen(url) as u:
                contents = u.read().decode("utf-8")
                json = get_json(contents)
                games = json["props"]["pageProps"]["games"]
                for game in games:
                    status = game["gameStatusText"]
                    if "final" not in status.lower():
                        cprint(f"[WARN] Game status not final ({status})", "yellow")
                        continue
                    away, home = game["awayTeam"], game["homeTeam"]
                    line = f"{str(date)},{game['gameId']},{away['teamSlug']},{away['score']},{home['teamSlug']},{home['score']}"
                    if not re.match("^\d+-\d+-\d+,\d+,\w+,\d+,\w+,\d+", line):
                        raise Exception(f"Game string error ({line})")
                    lines.append(line)
            with open(pathname, "w") as f:
                for line in lines:
                    f.write(f"{line}\n")
            time.sleep(1)

    # Concat all the files and delete the date files
    outpathname = f"{games_dir}/games.csv"
    with open(outpathname, "w") as outfile:
        for pathname in sorted(glob.glob(f"{games_dir}/*.csv")):
            if pathname == outpathname:
                continue
            with open(pathname, "r") as infile:
                shutil.copyfileobj(infile, outfile)
        for pathname in glob.glob(f"{games_dir}/*.csv"):
            if pathname != outpathname:
                Path(pathname).unlink()

if __name__ == "__main__":
    main()
