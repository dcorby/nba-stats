import sys
import re
import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge

"""
This is largely copied from this person's work...
https://jecutter.github.io/blog/rapm-model/
https://github.com/jecutter/nba-data-models/blob/master/Data_Modeling/RAPM_Model_NoPriors.ipynb
"""

base_dir = "/home/dmc7z/nba-stats"
game_dir = f"{base_dir}/data/game"

df_stints = pd.read_csv(f"{game_dir}/lineups.csv", index_col=0)
print(df_stints.head())

"""
Generate a (len(stints) x len(players))-dimensional matrix with
coeffs +1 for home players and -1 for away players
Also generate an array of length=len(stints) with the home margin
"""
def getCoeffsMatrix(df, players):
    home_margins = []
    rapm = np.zeros(shape=(len(df), len(players)), dtype=float)

    of = len(df)
    for i, tup in enumerate(df.iterrows(), 1):
        (idx, stint) = tup

        if i % 1000 == 0:
            print(f"Processing stint {i} of {of}...")

        home_margins.append(stint.h_pm100)

        _, players_i, __ = np.intersect1d(players, stint.home.split(":"), return_indices=True)
        rapm[i-1, players_i] = 1
        _, players_i, __ = np.intersect1d(players, stint.away.split(":"), return_indices=True)
        rapm[i-1, players_i] = -1

    return rapm, home_margins

players = set()
for i, row in df_stints.iterrows():
    [players.add(x) for x in row.away.split(":")]
    [players.add(x) for x in row.home.split(":")]
players = list(players)

rapm_matrix, home_margins = getCoeffsMatrix(df_stints, players)
df_rapm = pd.DataFrame(rapm_matrix, columns=players)
print(df_rapm.head())

# Calculate Player RAPM from Ridge Regression Coefficients
x_train = rapm_matrix
y_train = home_margins

# Create Ridge Regression model and find optimal hyperparameters
# with k-fold cross validation
ridge_reg = Ridge()
alphas = [1, 10, 50, 100, 500, 1000, 1500, 2000, 3000, 5000]
param_grid = { "alpha": alphas }
grid_search = GridSearchCV(ridge_reg, param_grid, cv=3)
grid_search.fit(x_train, y_train)
print("Optimized hyperparameters:", grid_search.best_params_)


"""
Test lambda parameters in the ridge regression in order to find a stable value.
Calculate the curves for the asymptotic max/min RAPM players to show stability of our choice of lambda
"""
alphas = [1, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000]
embiid = []
harden = []
tobias = []
max_arr = []
min_arr = []
rapm_alpha1 = []
rapm_alpha_best = []

for alph in alphas:
    ridge_reg = Ridge(alpha=alph)
    ridge_reg.fit(x_train, y_train)
    player_rapm = ridge_reg.coef_
    
    sorted_rapm = [x for _, x in sorted(zip(player_rapm, players), reverse=True)]
    
    for i, player in enumerate(sorted_rapm):
        if player == "203954":
            embiid.append(sorted(player_rapm, reverse=True)[i])
        elif player == "201935":
            harden.append(sorted(player_rapm, reverse=True)[i])
        elif player == "202699":
            tobias.append(sorted(player_rapm, reverse=True)[i])
    
    min_arr.append(sorted(player_rapm, reverse=True)[-1])
    max_arr.append(sorted(player_rapm, reverse=True)[0])
    
    if alph == 1:
        rapm_alpha1 = player_rapm
    elif alph == grid_search.best_params_["alpha"]:
        rapm_alpha_best = player_rapm

"""
Plot the lambda curves for the select players, along with min/max band spanning the RAPM range
Also plot the RAPM distribution for 2 choices of lambda
"""
"""
fig, ax = plt.subplots(1, 2, figsize=(20, 8))
plt.suptitle("Comparison of Ridge Regression Parameter Settings")

plt.axes(ax[0])
plt.fill_between(alphas, min_arr, max_arr, facecolor="black", alpha=0.3, label="Min-Max Band")
plt.plot(alphas, embiid, "ro-", label="Joel Embiid")
plt.plot(alphas, harden, "go-", label="James Harden")
plt.plot(alphas, tobias, "bo-", label="Tobias Harris")
plt.legend(loc="upper right", prop={ "size": 16 })
plt.axvline(x=grid_search.best_params_["alpha"], linestyle="--", c="k")
plt.xlabel("Lambda Parameter")
plt.ylabel("RAPM Rating")
"""


""" Get a player name lookup """
names = {}
with open(f"{game_dir}/game.csv", "r") as f:
    for line in f:
        if re.match("\d+,", line):
            tokens = line.split(",")
            name = tokens[1] + " " + tokens[2]
            names[tokens[0]] = name

"""
Make choice of lambda and perform final RAPM regression
Regression coefficients give scaled player RAPM values
"""
ridge_reg = Ridge(alpha=grid_search.best_params_["alpha"])
ridge_reg.fit(x_train, y_train)
player_rapm = ridge_reg.coef_

named = []
for i, rapm in enumerate(player_rapm):
    named.append({ "name": names[players[i]], "rapm": rapm })
for i, dct in enumerate(reversed(sorted(named, key=lambda d: d["rapm"])), 1):
    print(f"{i}. {dct['name']}, {dct['rapm']}")
    if i == 25:
        sys.exit()
    
    
    
