import sys
import re
import matplotlib.pyplot as plt
import numpy as np
import cairosvg
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from matplotlib.ticker import PercentFormatter
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FuncFormatter

base_dir = "/home/dmc7z/nba-stats"
work_dir = f"{base_dir}/shot-charts"
game_dir = f"{base_dir}/data/game"

def main():
    """ Compile data from game.csv """

    x, y, C = [], [], []
    with open(f"{game_dir}/game.csv", "r") as f:
        active = False
        for i, line in enumerate(f):
            if re.match("pbp", line):
                active = True
                continue
            if re.match("\d{10}", line):
                active = False
            if not active:
                continue
            if active:
                tokens = line.split(",")
                result = tokens[8].lower()
                if result not in ["made", "missed"]:
                    continue
                _x, _y = int(tokens[5]), int(tokens[6])
                if _y < 425:
                    x.append(_x + 250 + 5)
                    y.append(_y + 50)
                    fg2m = int(result == "made" and "3PT" not in line)
                    fg3m = int(result == "made" and "3PT" in line)
                    C.append(fg2m + 1.5*fg3m) 

    fig = plt.figure(figsize=(8,8))
    png = cairosvg.svg2png(file_obj=open(f"{work_dir}/court.svg", "r"))
    img = Image.open(BytesIO(png))
    width, height = img.size
    plt.imshow(img, extent=[0,510,0,510])

    # Make the plot
    # Halfcourt if aspect=15/14, but "To get approximately regular hexagons, choose..."
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.hexbin.html
    #RdYlGn
    hb = plt.hexbin(x, y, C=C, reduce_C_function=np.mean, mincnt=100, gridsize=33, bins="log", alpha=0.75, cmap="RdYlGn")
    ax = plt.gca()
    fmt = PercentFormatter()
    fmt = FuncFormatter(lambda x,_: "")
    cb = fig.colorbar(hb, ax=ax, shrink=0.5, format=fmt)
    plt.axis("off")
    plt.title("eFG%, 2020-21 through 2022-23")
    plt.show()

if __name__ == "__main__":
    main()
