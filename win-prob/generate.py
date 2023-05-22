import sys
import models.pre
import models.during

base_dir = "/home/dmc7z/nba-stats"
game_dir = f"{base_dir}/data/game"

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
