import sys
import glob
import pprint
pp = pprint.PrettyPrinter(indent=2, compact=True)

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
              id: { name: <str>, starter: <bool>, seconds: <int> },
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
            id, last, lastI, starter, seconds = (
                x[0], x[2], x[3], bool(x[4]), 0 if not x[12] else int(x[12].split(":")[0])*60 + int(x[12].split(":")[1]))
            players[team]["players"][id] = {
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
    
def set_lineups(plays, players):
    """ Compile the lineups """
    def get_player(name, team):
        found = []
        for id in players[team]["players"]:
            if name in [players[team]["players"][id]["lastI"], players[team]["players"][id]["last"]]:
                found.append({ "name": name, "id": id })
        if len(found) > 1:
            raise Exception(f"Multiple players found (team={team}, players={found})")
        if len(found) == 1:
            return found[0]["id"]
        # Catch some breaking exceptions
        id = helper.force_player(name)
        if id:
            return id
        pp.pprint(players)
        raise Exception(f"Player not found (team={team},name={name})")

    def get_team(tricode):
        for team in players:
            if helper.get_tricode(players[team]["team"]) == tricode:
                return team
        raise Exception(f"Team not found ({tricode})")

    # Iterate through plays
    #lineups = { "away": set(), "home": set() }
    for i, play in enumerate(plays):
        print(play)
        #print(play["actionType"], play["subType"], play["description"])
        #print("\n")
        play["lineups"] = { "away": set(), "home": set() }
        # Set the starting lineup
        if i == 0:
            for team in ["away", "home"]:
                lineup = { k:v for (k,v) in players[team]["players"].items() if v["starter"] }.keys()
                play["lineups"][team] = set(lineup)
        else:
            # Handle period ends
            if play["subType"] == "end":
                play["lineups"][team] = set()
            # Carry over from previous play
            else:
                for team in ["away", "home"]:
                    play["lineups"][team] = plays[i-1]["lineups"][team]
                # Handle subs

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

    
    

def main():
    for pathname in glob.glob(f"{game_dir}/*.csv"):
        print(pathname)
        with open(pathname, "r") as f:
            print(pathname)
            id = pathname.replace(".csv", "").split("/")[-1]
            if id in ["0032100001", "0032200006", "0032200005", "0032200001"]: # All Star competitions
                continue
            players = get_players(f)
            plays = get_plays(f)
            plays = set_lineups(plays, players)
            
            
if __name__ == "__main__":
    main()
