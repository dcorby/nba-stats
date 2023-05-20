import matplotlib.pyplot as plt
import numpy as np
import cairosvg
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

work_dir = "/home/dmc7z/nba-stats/shot-charts"

def main():
    """ Compile data from game.csv """

    png = cairosvg.svg2png(file_obj=open(f"{work_dir}/court.svg", "r"))
    img = Image.open(BytesIO(png))
    width, height = img.size
    print(width, height)
    plt.axis("off")
    plt.imshow(img, extent=[0,510,0,510])

    x = np.random.normal(size=50000)
    y = np.random.normal(size=50000)
    #y = (x * 3 + np.random.normal(size=50000)) * 5
    print(np.min(x))
    print(np.max(x))
    print(np.min(y))
    print(np.max(y))
     
    # Make the plot
    # Halfcourt if aspect=15/14, but "To get approximately regular hexagons, choose..."
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.hexbin.html
    plt.hexbin(x, y, mincnt=1, gridsize=(23,13))
    plt.show()
     
    # We can control the size of the bins:
    #plt.hexbin(x, y, gridsize=(150,150) )
    #plt.show()

if __name__ == "__main__":
    main()
