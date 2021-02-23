import networkx as nx
import matplotlib.pyplot as plt

from ant import Ant
from utils import window


"""
Today:
* deposition function
"""


class Optimize:
    def __init__(self, coordinates, num_ants,
                 radius=None, 
                 alpha=0.5,
                #  deposition_rate=1.0, 
                 evaporation_rate=0.1):
        """TKTK"""
        self.G = self.make_graph(coordinates, radius=radius)
        if radius:
            self.radius = radius
        else:
            max_dist = max(e[2]["distance"] for e in self.G.edges(data=True))
            self.radius = max_dist + 1  #prevent 0.0 probability

        self.alpha = alpha

        self.ants = [Ant(self.G, self.radius, self.alpha) for _ in range(num_ants)]
        # self.deposition_rate = deposition_rate
        self.evaporation_rate = evaporation_rate
        
        self.current_shortest_distance = \
            sum(e[2]["distance"] for e in self.G.edges(data=True))
        self.current_shortest_path = []
        self.iteration_count = 0
        self.iteration_best_history = []
        self.global_best_history = []
        self.unique_paths = []


    def optimize(self, num_iterations=20):
        for _ in range(num_iterations):
            # fastest_ant = self.release_ants()
            self.release_ants()
            self.update_pheronome_trails()
            self.update_solution()
            the_solver_has_converged = self.convergence_detection()
            if the_solver_has_converged:
                break
            # self.update_pheronome_trails(fastest_ant)
            # self.update_solution(fastest_ant)


    def release_ants(self):
        for ant in self.ants:
            ant.traverse_graph()
        # fastest_ant = sorted(self.ants, key=lambda a: a.distance_traveled)[0]
        # return fastest_ant


    def update_pheronome_trails(self):
        """
        1. Each ant deposits pheromone based on how short their route was.
        2. Evaporate pheromone from all paths
        """
        for ant in self.ants:
            deposition_amount = self.calculate_deposition_amount(ant)

            for n1, n2 in window(ant.path):
                self.G[n1][n2]["pheromone"] += deposition_amount

        # Deposit pheromone on the fastest path
        # for n1, n2 in window(fastest_ant.path):
        #     # amount = self.gl
        #     self.G[n1][n2]["pheromone"] += self.deposition_rate

        # Evaporate pheromone on all paths
        for edge in self.G.edges(data=True):
            edge[2]["pheromone"] = (1-self.evaporation_rate) * edge[2]["pheromone"]
            # edge[2]["pheromone"] -= self.evaporation_rate
            # if edge[2]["pheromone"] < 0:
            #     edge[2]["pheromone"] = 0


    def calculate_deposition_amount(self, ant):
        ph = self.current_shortest_distance / ant.distance_traveled
        ph = ph**2
        return ph


    def update_solution(self):
        fastest_ant = sorted(self.ants, key=lambda a: a.distance_traveled)[0]
        self.iteration_best_history.append(fastest_ant.distance_traveled)
        # print(f"The fastest ant completed its loop in {fastest_ant.distance_traveled} units.")
        if fastest_ant.distance_traveled < self.current_shortest_distance:
            self.current_shortest_distance = fastest_ant.distance_traveled
            self.current_shortest_path = fastest_ant.path


    def convergence_detection(self):
        """Return True if the solver has converged or stagnated"""
        self.iteration_count += 1
        self.global_best_history.append(self.current_shortest_distance)
        self.unique_paths.append(len(set(a.distance_traveled for a in self.ants)))
        if self.iteration_count > 100:
            if self.iteration_count % 20 == 0:
                if len(set(self.global_best_history[-100:])) == 1:
                    # The path is not getting any shorter
                    print('The solver has "converged".')
                    print(f'The ants are following {self.unique_paths[-1]} differnt path(s).')
                    return True
                if len(set(self.unique_paths[-20:])) == 1:
                    print("Ants are all following the same path.")
                    return True
        return False


    #########################################################################    
    ######################## Attached Plotting Tools ########################
    #########################################################################


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
        _, ax = plt.subplots()
        ax.plot(self.global_best_history, label="Global Best", color="green", lw=1)
        ax.scatter(range(self.iteration_count), self.iteration_best_history, alpha=0.6, s=2, label="Iteration Best")
        plt.xlabel("Iteration")
        plt.ylabel("Length of Shortest Path")
        plt.title("Are the Ants Getting Faster?")
        plt.legend()


    def plot_greediness(self):
        ratios = [a.first_pick_ratio*100 for a in self.fastest_ants]
        plt.plot(ratios)
        plt.xlabel("Iteration")
        plt.ylabel("Percent")
        plt.title("Greediness\nPercent of times the fastest ant chose the most probable node")


def euclidean_distance(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def triangular_number(n):
    if n == 0:
        return n
    else:
        return n + triangular_number(n-1)