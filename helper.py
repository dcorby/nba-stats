import re

action = ["clock", "period", "teamTricode", "personId", "playerName", "xLegacy", "yLegacy", "shotDistance", "shotResult", "isFieldGoal", "scoreHome", "scoreAway", "description", "actionType", "subType"]

special_games = ["0032100004", "0032100005", "0032100006", "0032000001", "0032200001", "0032200004", "0032200005", "0032200006", "0032100001"]

def get_tricode(name):
    teams = {
      "warriors": "GSW", "lakers"  : "LAL", "celtics": "BOS", "heat"        : "MIA", "pistons"  : "DET",
      "hornets" : "CHA", "pelicans": "NOP", "bucks"  : "MIL", "hawks"       : "ATL", "mavericks": "DAL",
      "thunder" : "OKC", "sixers"  : "PHI", "kings"  : "SAC", "grizzlies"   : "MEM", "cavaliers": "CLE",
      "wizards" : "WAS", "magic"   : "ORL", "suns"   : "PHX", "pacers"      : "IND", "knicks"   : "NYK",
      "blazers" : "POR", "nuggets" : "DEN", "raptors": "TOR", "nets"        : "BKN", "bulls"    : "CHI",
      "rockets" : "HOU", "jazz"    : "UTA", "spurs"  : "SAS", "timberwolves": "MIN", "clippers" : "LAC"
    }
    if name not in teams:
        raise Exception(f"get_tricode() team not found (team={name})")
    return teams[name]

def get_other(play):
    m = re.search("PTS\) \((.*?) \d+ AST\)", play["description"])
    if m:
        return m.group(1)
    return None

def get_subs(play):
    m = re.search("SUB: (.*?) FOR (.*?)$", play["description"])
    return m.group(2), m.group(1)

def process_lineup(play):
    """ There will always be a sub after an ejection """
    if (play["actionType"].strip() in ["Timeout", "Instant Replay", "Ejection"] 
        or play["subType"].strip() in ["Normal Rebound", "Unknown", "end", "start", "Shot Clock Turnover", "Technical", "Delay Of Game", 
                                "8 Second Violation", "5 Second Violation", "Delay Technical", "Non-Unsportsmanlike Technical", 
                                "Excess Timeout Technical", "Excess Timeout Turnover", "Too Many Players Technical", "Too Many Players Turnover"]):
        return False
    return True

def force_player(name):
    if name == "Co. Martin":
        return "1628998"
    if name == "Kanter":
        return "202683"
    if name == "Dowtin":
        return "1630288"
    if name == "Jal. Williams":
        return "1631114"
    if name == "Jay. Williams":
        return "1631119"
    if name == "Ja. Green":
        return "203210"
    if name == "Je. Green":
        return "201145"
    if name == "Ca. Martin":
        return "1628997"
    if name == "Mason":
        return "1628412"
    return None

