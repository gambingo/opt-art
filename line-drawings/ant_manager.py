import networkx as nx
import matplotlib.pyplot as plt

from ant import Ant
from utils import window


"""
Load image from stippling
Create graph from list of points
    - Include radius, how far each ant can see
    – What if we use this radius to calculate distance percentages. 
        – This radius is the max distance. 
        – That could limit the zero prob problem, and normalize probabilities across teh graph
Release ants
log fastest route and deposit pheromone
    - evaporation rate
    - deposition rate
    (If they are constant rates then this is easy)
repeat

Interesting interesting interesting. Expectedly, the radius made it so there 
were no more adjacent nodes but still nodes left to visit. Unexpectedly, the 
path couldn't be closed at the end. Let's leave the radius out for now and 
include it again once we're running this for higher nodes.
"""


class Optimize:
    def __init__(self, coordinates, num_ants,
                 radius=None, 
                 deposition_rate=1.0, 
                 evaporation_rate=0.1):
        """TKTK"""
        self.G = self.make_graph(coordinates, radius=radius)
        if radius:
            self.radius = radius
        else:
            max_dist = max(e[2]["distance"] for e in self.G.edges(data=True))
            self.radius = max_dist + 1  #prevent 0.0 probability

        self.ants = [Ant(self.G, self.radius) for _ in range(num_ants)]
        self.deposition_rate = deposition_rate
        self.evaporation_rate = evaporation_rate
        self.fastest_ants = []
        self.current_shortest_distance = \
            sum(e[2]["distance"] for e in self.G.edges(data=True))
        self.current_shortest_path = []


    def optimize(self, num_iterations=20):
        for _ in range(num_iterations):
            fastest_ant = self.release_ants()
            self.update_pheronome_trails(fastest_ant)
            self.update_solution(fastest_ant)


    def release_ants(self):
        for ant in self.ants:
            ant.traverse_graph()
        fastest_ant = sorted(self.ants, key=lambda a: a.distance_traveled)[0]
        return fastest_ant


    def update_pheronome_trails(self, fastest_ant):
        # Deposit pheromone on the fastest path
        for n1, n2 in window(fastest_ant.path):
            self.G[n1][n2]["pheromone"] += self.deposition_rate

        # Evaporate pheromone on all paths
        for edge in self.G.edges(data=True):
            edge[2]["pheromone"] -= self.evaporation_rate
            if edge[2]["pheromone"] < 0:
                edge[2]["pheromone"] = 0


    def update_solution(self, fastest_ant):
        self.fastest_ants.append(fastest_ant)
        # print(f"The fastest ant completed its loop in {fastest_ant.distance_traveled} units.")
        if fastest_ant.distance_traveled < self.current_shortest_distance:
            self.current_shortest_distance = fastest_ant.distance_traveled
            self.current_shortest_path = fastest_ant.path


    def make_graph(self, chosen_points, radius):
        """Make the network graph from the list of coordinates"""
        G = nx.Graph()
        node_coords = {ii:(p[0], p[1]) for ii,p in enumerate(chosen_points)}
        node_ids = {ii:ii for ii,_ in enumerate(chosen_points)}

        # Nodes
        G.add_nodes_from(node_coords.keys())
        nx.set_node_attributes(G, node_coords, "coords")
        nx.set_node_attributes(G, node_ids, "id")

        # Edges
        for ii in G.nodes():
            for jj in G.nodes():
                if ii > jj:
                    n1, n2 = G.nodes[ii]["coords"], G.nodes[jj]["coords"]
                    d = euclidean_distance(n1, n2)
                    if radius:
                        if d < radius:
                            G.add_edge(ii, jj, distance=d, pheromone=0)
                    else:
                        G.add_edge(ii, jj, distance=d, pheromone=0)

        msg = f"The graph has {len(G.nodes)} nodes and {len(G.edges)} edges."
        print(msg)
        return G


    def plot_convergence(self):
        """Optimistic function name"""
        path_distances = [ant.distance_traveled for ant in self.fastest_ants]
        # plt.bar(range(len(path_distances)), path_distances)
        plt.plot(path_distances)
        plt.xlabel("Iteration")
        plt.ylabel("Length of Shortest Path")
        plt.title("Are the Ants Getting Faster?")


    def plot_first_pick_ratios(self):
        ratios = [a.first_pick_ratio*100 for a in self.fastest_ants]
        plt.plot(ratios)
        plt.xlabel("Iteration")
        plt.ylabel("Percent")
        plt.title("First Pick Ratios\nPercent of times the fastest ant chose the most probable node")


def euclidean_distance(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def triangular_number(n):
    if n == 0:
        return n
    else:
        return n + triangular_number(n-1)