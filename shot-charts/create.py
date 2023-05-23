import sys
import re
import matplotlib.pyplot as plt
import numpy as np
import cairosvg
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

base_dir = "/home/dmc7z/nba-stats"
work_dir = f"{base_dir}/shot-charts"
game_dir = f"{base_dir}/data/game"

def main():
    """ Compile data from game.csv """

    x, y = [], []
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
                if tokens[8].lower() not in ["made", "missed"]:
                    continue
                _x, _y = int(tokens[5]), int(tokens[6])
                if _y < 425:
                    x.append(_x + 250 + 5)
                    y.append(_y + 50)

    plt.figure(figsize=(8,8))
    png = cairosvg.svg2png(file_obj=open(f"{work_dir}/court.svg", "r"))
    img = Image.open(BytesIO(png))
    width, height = img.size
    plt.imshow(img, extent=[0,510,0,510])
    plt.axis("off")

    # Make the plot
    # Halfcourt if aspect=15/14, but "To get approximately regular hexagons, choose..."
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.hexbin.html
    plt.hexbin(x, y, mincnt=1, gridsize=33, alpha=0.75)
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    main()
