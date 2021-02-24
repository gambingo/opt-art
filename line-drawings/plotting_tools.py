from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from utils import window


class Analyze():
    """A collection of plotting tools to analyze and instance of Optimize"""
    
    def __init__(self, optimize):
        self.G = optimize.G
        self.radius = optimize.radius
        self.ants = optimize.ants
        self.current_shortest_path = optimize.current_shortest_path
        self.global_best_history = optimize.global_best_history


    def plot_path(self, show_pheromone=False):
        img = Image.new("RGBA", (512,512), color=(255,255,255,0))
        draw = ImageDraw.Draw(img)

        path = self.current_shortest_path
        g = self.G

        if show_pheromone:
            max_pheromone = max(e[2]["pheromone"] for e in g.edges(data=True))

        # Draw path
        for n1, n2 in window(path):
            y1, x1 = g.nodes[n1]["coords"]
            y2, x2 = g.nodes[n2]["coords"]

            if show_pheromone:
                perc = g[n1][n2]["pheromone"]/max_pheromone
                fill = (0, 0, 0, int(255*perc))
            else:
                fill = (0, 0, 0, 255)

            draw.line([(x1, y1), (x2, y2)], fill=fill)

        for n in g.nodes(data=True):
            y, x = n[1]["coords"]
            draw.regular_polygon((x, y, 1), fill=(0,0,0,255), n_sides=30)

        return img


    def plot_graph(self, show_pheromone=False):
        img = Image.new("RGBA", (512,512), color=(255,255,255,0))
        draw = ImageDraw.Draw(img)

        # path = self.current_shortest_path
        g = self.G

        if show_pheromone:
            max_pheromone = max(e[2]["pheromone"] for e in g.edges(data=True))

        # Draw path
        for n1, n2, data in g.edges(data=True):
            y1, x1 = g.nodes[n1]["coords"]
            y2, x2 = g.nodes[n2]["coords"]

            if show_pheromone:
                perc = data["pheromone"]/max_pheromone
                fill = (0, 0, 0, int(255*perc))
            else:
                fill = (0, 0, 0, 255)

            draw.line([(x1, y1), (x2, y2)], fill=fill)

        for n in g.nodes(data=True):
            y, x = n[1]["coords"]
            draw.regular_polygon((x, y, 1), fill=(0,0,0,255), n_sides=30)

        if show_pheromone:
            # Let's also include a histogram of pheromone levels
            ph_levels = [e[-1]["pheromone"] for e in g.edges(data=True)]
            plt.hist(ph_levels)
            plt.title("Pheromone Levels Throughout the Graph")
            plt.xlabel("Pheromone Build Up")
            plt.ylabel("No. Paths")

        return img


    def plot_convergence(self):
        """Optimistic function name"""
        _, ax = plt.subplots()
        ax.plot(self.global_best_history, label="Global Best", color="green", lw=1)
        ax.scatter(range(self.iteration_count), self.iteration_best_history, alpha=0.6, s=2, label="Iteration Best")
        plt.xlabel("Iteration")
        plt.ylabel("Length of Shortest Path")
        plt.title("Are the Ants Getting Faster?")
        plt.legend()


    def plot_greediness(self):
        """TODO: Base this function off actual history"""
        ratios = [a.first_pick_ratio*100 for a in self.fastest_ants]
        plt.plot(ratios)
        plt.xlabel("Iteration")
        plt.ylabel("Percent")
        plt.title("Greediness\nPercent of times the fastest ant chose the most probable node")


    def plot_unique_paths(self):
        _, ax = plt.subplots()
        ax.plot(self.unique_paths)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.title("Unique Paths")
        plt.xlabel("Iteration")
        plt.ylabel("No. Unqiue Paths Ants are Following")
        plt.grid(True)