import sys
import models.pre
import models.during

base_dir = "/home/dmc7z/nba-stats"
game_dir = f"{base_dir}/data/game"

def get_pbp():
    with open(f"{game_dir}/game.csv", "r") as f:
        gid = None
        pbp = False
        for line in f:
            # Set the gid
            m = re.search("^(\d{10})\s", line)
            if m:
                pbp = False
                gid = m.group(1) if m.group(1) in games else None
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
                clock = clock.replace("PT", "").split(".")[0]
                minutes, seconds = [int(x) for x in clock.split("M")]
                sec_rem = 4*12*60 - (12*60*(period-1)) - (12*60 - (minutes*60 + seconds))
                # Backfill
                if len(games[gid]["pbp"]) > 0:
                    prev = games[gid]["pbp"][-1]
                    diff = prev["sec_rem"] - sec_rem
                    if diff > 1:
                        for add, i in enumerate(range(0, diff)):
                            games[gid]["pbp"].append({ "margin": prev["margin"], "sec_rem": prev["sec_rem"] - add })
                games[gid]["pbp"].append({ "margin": margin, "sec_rem": sec_rem })

    return games

def main():
    # Get the predictors and models
    print("Getting models.pre...")
    gids, pre = models.pre.get_model()
    print("Getting models.during...")
    games, during = models.during.get_models()

    for i, gid in enumerate(gids):
        print(f"Game={gid}")
        pre_proba = pre["model"].predict_proba([pre["X"][i]])
        print(f"Pre-game win prob={pre_proba}")
        #for sec_rem in during:
        for play in games[gid]["pbp"]:
            margin, sec_rem = play["margin"], play["sec_rem"]
            if sec_rem == 0:
                continue
            X = [[ 1, margin, sec_rem, margin*sec_rem ]]
            during_proba = during[sec_rem]["model"].predict_proba(X)
            print(f"In-game win prob ({sec_rem} sec_rem/{margin} margin)={during_proba}")
        sys.exit()

if __name__ == "__main__":
    main()
