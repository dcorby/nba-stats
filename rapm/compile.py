import sys
import glob
import re
import io
import pprint
pp = pprint.PrettyPrinter(indent=2, compact=True)
from termcolor import colored, cprint

# relative imports won't work 
# https://docs.python.org/3/tutorial/modules.html#packages "modules intended for use..."
sys.path.append("..")
import helper

base_dir = "/home/dmc7z/nba-stats"
games_dir = f"{base_dir}/data/games"
game_dir = f"{base_dir}/data/game"

def get_players(f):
    """ Collect players by team and return a dict like
        dict = {
          away: {
            team: 
            players: {
              id: { last: <str>, lastI: <str>, starter: <bool>, seconds: <int> },
            }
            ...
          },
    """
    players = {}
    team = None
    for line in f:
        if any(line.strip().startswith(x) for x in ["away", "home"]):
            team, name = line.strip().split(",")
            players[team] = { "team": name, "players": {}}
            continue
        if line.strip() == "pbp":
            return players
        if team:
            x = line.split(",")
            pid, last, lastI, starter, seconds = (
                x[0], x[2], x[3], bool(x[4]), 0 if not x[12] else int(x[12].split(":")[0])*60 + int(x[12].split(":")[1]))
            players[team]["players"][pid] = {
                "last": last,
                "lastI":  lastI,
                "starter": starter,
                "seconds": seconds
            }

def get_plays(f):
    """ Collect plays in a list of dicts, apply an origId, 
        and push subs to the end of each clock
    """
    plays = []
    subs = []
    prev_time = None
    for i, line in enumerate(f):
        # Skip play text errors
        if "Adair BLOCK (1 BLK)" in line:
            continue
        tokens = line.strip().split(",")
        play = { "origId": i }
        for j, token in enumerate(helper.action):
            play[token] = tokens[j]
        if play["clock"] != prev_time:
            for sub in subs:
                plays.append(sub)
            subs = []
        if play["actionType"] == "Substitution":
            subs.append(play)
        else:
            plays.append(play)
        prev_time = play["clock"]
    return plays
    
def set_lineups(gid, plays, players):
    """ Compile the lineups """
    def get_player(name, team):
        found = []
        for pid in players[team]["players"]:
            if name in [players[team]["players"][pid]["lastI"], players[team]["players"][pid]["last"]]:
                found.append({ "name": name, "id": pid })
        if len(found) > 1:
            raise Exception(f"Multiple players found (team={team}, players={found})")
        if len(found) == 1:
            return found[0]["id"]
        # Catch some breaking exceptions
        pid = helper.force_player(name)
        if pid:
            return pid
        pp.pprint(players)
        raise Exception(f"Player not found (team={team},name={name})")

    def get_team(tricode):
        for team in players:
            if helper.get_tricode(players[team]["team"]) == tricode:
                return team
        raise Exception(f"Team not found ({tricode})")

    # Iterate through plays
    for i, play in enumerate(plays):
        # Set the starting lineup
        play["lineups"] = {}
        if i == 0:
            for team in ["away", "home"]:
                lineup = { k:v for (k,v) in players[team]["players"].items() if v["starter"] }.keys()
                play["lineups"][team] = set(lineup)
        else:
            # Handle period starts
            if play["subType"] == "start":
                for team in ["away", "home"]:
                    play["lineups"][team] = set()
            else:
                # Carry over from previous play
                for team in ["away", "home"]:
                    play["lineups"][team] = plays[i-1]["lineups"][team].copy()
                # Handle subs
                if play["actionType"] == "Substitution":
                    team = get_team(play["teamTricode"])
                    remove, add = helper.get_subs(play)
                    player = get_player(remove, team)
                    if player in play["lineups"][team]:
                        play["lineups"][team].remove(player)
                    player = get_player(add, team)
                    play["lineups"][team].add(player)
                else:
                    # Add the primary
                    if helper.process_lineup(play):
                        team = get_team(play["teamTricode"])
                        primary = play["personId"]
                        play["lineups"][team].add(primary)
                        # Add the other
                        other = helper.get_other(play)
                        if other:
                            # Assume other players are on active team
                            player = get_player(other, team)
                            play["lineups"][team].add(player)

    # Iterate through plays in reverse
    for i, play in enumerate(reversed(plays), 1):
        i = len(plays) - i
        if i == len(plays) - 1:
            continue
        # Skip end of periods
        if plays[i+1]["subType"] != "start":
            for team in ["away", "home"]:
                this = play["lineups"][team]
                last = plays[i+1]["lineups"][team]
                diff = last.difference(this)
                for player in diff:
                    play["lineups"][team].add(player)
            # Handle subs
            if plays[i+1]["actionType"] == "Substitution":
                team = get_team(plays[i+1]["teamTricode"])
                remove, add = helper.get_subs(plays[i+1])
                player = get_player(remove, team)
                play["lineups"][team].add(player)
                player = get_player(add, team)
                play["lineups"][team].remove(player)

    # Patch some known errors
    # Bol Bol error in this game
    if gid == "0022100151":
        for play in plays:
            if "1629626" in play["lineups"]["home"]:
                play["lineups"]["home"].remove("1629626")
    # Steph Curry error
    if gid == "0022100750":
        for play in plays:
            if play["origId"] in [505,506,507,512,513,514]:
                play["lineups"]["home"].remove("202691")
    # Jimmy Butler error
    if gid == "0022200974":
        for play in plays:
            if play["origId"] in [463,464,465,466,467,470,471]:
                play["lineups"]["home"].remove("202710")

    return plays

def summarize(num, plays, players):
    def get_seconds(final):
        seconds = {}
        for i, play in enumerate(plays):
            #if num == 3284:
            #    print(play["origId"], play["lineups"])
            def get_seconds(play, next_play):
                if play["clock"] == "PT00M00.00S":
                    return 0.0
                # Now
                clock = play["clock"]
                m = re.search("(\d+)M(\d+\.\d+)S", clock)
                now = int(m.group(1))*60 + float(m.group(2))
                # End of play
                clock = next_play["clock"]
                m = re.search("(\d+)M(\d+\.\d+)S", clock)
                end = int(m.group(1))*60 + float(m.group(2))
                total = now - end
                return total
            
            if i == len(plays) - 1:
                break
            sec = get_seconds(play, plays[i+1])
            for team in ["away", "home"]:
                for player in play["lineups"][team]:
                    seconds[player] = seconds.get(player, 0) + sec
        return seconds

    # Patch lineups
    seconds = get_seconds(False)
    for team in ["away", "home"]:
        for pid in players[team]["players"]:
            player = players[team]["players"][pid]
            actual = player["seconds"]
            if actual == 0:
                continue
            computed = seconds[pid]
            diff = computed - actual
            # Patch on stints
            if diff > 5:
                for play in plays:
                    if len(play["lineups"][team]) > 5 and pid in play["lineups"][team]:
                        play["lineups"][team].remove(pid)
            # Patch off stints
            if diff < 5:
                for play in plays:
                    if len(play["lineups"][team]) < 5:
                        play["lineups"][team].add(pid)

    # Print summary
    seconds = get_seconds(True)
    for team in ["away", "home"]:
        for pid in players[team]["players"]:
            player = players[team]["players"][pid]
            actual = player["seconds"]
            if actual == 0:
                continue
            computed = seconds[pid]
            diff = computed - actual
            color = "red" if abs(diff) > 5 else None
            cprint(f"Player={pid}/{player['lastI']}, Actual={actual}, Computed={computed}", color)

def main():
    count = len(re.findall("\d{10}", open(f"{games_dir}/games.csv", "r").read()))
    def parse(num, string):
        gid = string[0:10]
        print(f"Parsing game num {num} of {count} ({gid})")
        f = io.StringIO(string)
        players = get_players(f)
        plays = get_plays(f)
        plays = set_lineups(gid, plays, players)
        summarize(num, plays, players)
        #if num == 3284:
        #    sys.exit()
    with open(f"{game_dir}/game.csv", "r") as f:
        num = 1
        string = ""
        for line in f:
            if string and re.match("\d{10}", line):
                parse(num, string)
                num += 1
                string = ""
            string += line
        parse(num, string)
            
if __name__ == "__main__":
    main()
