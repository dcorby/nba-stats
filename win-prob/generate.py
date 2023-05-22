import sys
import models.pre
import models.during
import matplotlib.pyplot as plt
import numpy as np

base_dir = "/home/dmc7z/nba-stats"
game_dir = f"{base_dir}/data/game"

"""
games to test:
https://www.nba.com/game/ind-vs-mia-0022200825/game-charts
https://www.nba.com/game/sac-vs-hou-0022200827/game-charts
https://www.nba.com/game/gsw-vs-por-0022200830/game-charts
"""

def make_plot(game, probs):
    x = list(range(0, 2800+1))
    y_a, y_h = [], []
    for sec_rem in x:
        if sec_rem == 0:
            continue
        y_a.append(probs["during"][sec_rem][0][0])
        y_h.append(probs["during"][sec_rem][0][1])
    y_a.append(probs["pre"][0][0])
    y_h.append(probs["pre"][0][1])
    plt.figure(figsize=(8, 5))
    plt.plot(x, y_a, color="blue", linewidth=2.0)
    plt.plot(x, y_h, color="red", linewidth=2.0)
    plt.xlim([0, 2800])
    plt.ylim([0.0, 1.0])
    ax = plt.gca()    # gca="get current axes"
    ax.invert_xaxis()
    plt.show()

    sys.exit()

def main():
    # Get the predictors and models
    print("Getting models.pre...")
    gids, pre = models.pre.get_model()
    print("Getting models.during...")
    games, during = models.during.get_models()

    probs = { "pre": None, "during": {} }
    for i, gid in enumerate(gids):
        print(f"Game={gid}")
        pre_proba = pre["model"].predict_proba([pre["X"][i]])
        probs["pre"] = pre_proba
        print(f"Pre-game win prob={pre_proba}")
        #for sec_rem in during:
        game = games[gid]
        date, away, home = game["date"], game["away"], game["home"]
        for play in game["pbp"]:
            margin, sec_rem = play["margin"], play["sec_rem"]
            if sec_rem == 0:
                continue
            X = [[ 1, margin, sec_rem, margin*sec_rem ]]
            during_proba = during[sec_rem]["model"].predict_proba(X)
            print(f"In-game win prob ({sec_rem} sec_rem/{margin} margin)={during_proba}")
            probs["during"][sec_rem] = during_proba
        make_plot(game, probs)

if __name__ == "__main__":
    main()
