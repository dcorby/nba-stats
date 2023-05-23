import sys
import models.pre
import models.during
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

base_dir = "/home/dmc7z/nba-stats"
game_dir = f"{base_dir}/data/game"

colors = {
  "celtics":   "#007a33", "mavericks": "#00538c",    "rockets": "#ce1141", "pelicans": "#85714d",  "warriors": "#1d428a",
  "raptors":   "#ce1141", "nuggets": "#8b2131",      "jazz": "#00471b",    "kings": "#5a2d81",     "lakers": "#552583",
  "sixers" :   "#006bb6", "timberwolves": "#236192", "hornets": "#00788c", "bulls": "#ce1141",     "knicks": "#f58426",
  "wizards":   "#e31837", "thunder": "#007ac1",      "hawks": "#c1d32f",   "pacers": "#fdbb30",    "nets": "#000000",
  "heat"   :   "#f9a01b", "suns": "#e56020",         "magic": "#0077c0",   "bucks": "#00471b",     "clippers": "#1d428a",
  "cavaliers": "#860038", "pistons": "#1d42ba",      "spurs": "#c4ced4",   "grizzlies": "#5d76a9", "blazers": "#e03a3e"
}

"""
games to test:
https://www.nba.com/game/ind-vs-mia-0022200825/game-charts
https://www.nba.com/game/sac-vs-hou-0022200827/game-charts
https://www.nba.com/game/gsw-vs-por-0022200830/game-charts
https://www.nba.com/game/phi-vs-bos-0022200824/game-charts
"""
GID = "0022200830"

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
    plt.plot(x, y_a, color=colors[game["away"]], linewidth=2.0)
    plt.plot(x, y_h, color=colors[game["home"]], linewidth=2.0)
    plt.xlim([0, 2800])
    plt.ylim([0.0, 1.0])
    ax = plt.gca()    # gca="get current axes"
    ax.invert_xaxis()
    plt.title(f"Win Prob, {game['away']} @ {game['home']}, {game['date']}")
    plt.xlabel("Seconds remaining")
    plt.ylabel("Win Prob")
    #ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    fmt = ticker.FuncFormatter(lambda y, _: "{:.0%}".format(y))
    ax.yaxis.set_major_formatter(fmt)
    plt.legend([game["away"], game["home"]], loc=0, frameon=True)
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
        if GID and GID != gid:
            continue
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
            # Get the weighted probability
            prob = during_proba
            prob[0][0] = sec_rem/2800*probs["pre"][0][0] + (2800-sec_rem)/2800*prob[0][0]
            prob[0][1] = sec_rem/2800*probs["pre"][0][1] + (2800-sec_rem)/2800*prob[0][1]
            probs["during"][sec_rem] = prob
                
        make_plot(game, probs)

if __name__ == "__main__":
    main()
