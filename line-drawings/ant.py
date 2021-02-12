import random
from copy import copy
from warnings import warn

import pandas as pd


class Ant:
    def __init__(self, graph, radius=None, logging=False):
        self.G = graph
        self.radius = radius
        self.first_picks = []
        self.logging = logging
        if logging:
            self.history = {}
        

    def reset_memory(self):
        self.distance_traveled = 0
        self.path = []
        self.max_ph = max(e[2]["pheromone"] for e in self.G.edges(data=True))


    def traverse_graph(self):
        """
        How to traverse the graph:
            1. Get dropped onto a random node  
                1.1 Record that you've been to this node.  
            2. Assess all the possible paths (determine probabilities) 
            3. Choose another node  
                2.1 Record Distance  
                2.2 Record that you've been to this node.  
            4. When you've been to all nodes, go back to the start.
        """
        # Starting node
        self.reset_memory()
        curr_loc = random.choice(self.G.nodes())["id"]
        self.path.append(curr_loc)

        # Traverse
        while len(self.path) < len(self.G.nodes):
            # Asses possible paths
            adj_nodes = [i for i in self.G[curr_loc] if i not in self.path]
            probs = self.determine_selection_probabilities(curr_loc, adj_nodes)

            # Choose new location
            next_loc = random.choices(adj_nodes, weights=probs, k=1)[0]
            self.move_from(curr_loc, next_loc)
            
            ya_pick_the_first = next_loc == adj_nodes[probs.index(max(probs))]
            self.first_picks.append(ya_pick_the_first)

            curr_loc = next_loc

        # After visiting every node, return to starting location
        self.move_from(curr_loc, self.path[0])
        self.first_pick_ratio = sum(self.first_picks)/len(self.first_picks)


    def move_from(self, curr_loc, new_loc):
        self.path.append(new_loc)
        self.distance_traveled += self.G[curr_loc][new_loc]["distance"]


    def determine_selection_probabilities(self, curr_node, adj_nodes):
        """
        Determine the probabilities for moving from the current node to any of
        the available adjacent nodes.
        """
        distances = [self.G[curr_node][ii]["distance"] for ii in adj_nodes]
        percents = [1 - d/self.radius for d in distances]
        distance_probs = [p/sum(percents) for p in percents]

        # I don't like this as is. I want this to be like real ants.
        # pheromone probs should be relative to a constant maximum
        # Calculating probs from the percent of the max isn't gonna work
        # For the obvious paths, the pheromone levels constantly increase
        # So the max is runaway
        # Then the lower levels probs get smaller
        # So, ok, maybe it should be out of a local max?
        # let's read
        ph_levels = [self.G[curr_node][ii]["pheromone"] for ii in adj_nodes]
        ph_probs = [p/sum(ph_levels) if sum(ph_levels) else 0 for p in ph_levels]

        # I want them to have equal weight. They both need to be normalized
        # distance_probs = [d/max(distance_probs) for d in distance_probs]
        # ph_probs = [p/max(ph_probs) if max(ph_probs)>0 else 0 for p in ph_probs]

        probabilities = [d+p for d,p in zip(distance_probs, ph_probs)]
        
        # construct table for this node
        if self.logging:
            df = pd.DataFrame()
            df["Next Node"] = pd.Series(adj_nodes)
            df["Distances"] = pd.Series(distances)
            df["Distance Probs"] = pd.Series(distance_probs)
            df["Pheromone Levels"] = pd.Series(ph_levels)
            df["Pheromone Probs"] = pd.Series(ph_probs)
            df["Selection Probabilities"] = pd.Series(probabilities)
            df = df.set_index("Next Node")
            df = df.sort_values(by="Selection Probabilities", ascending=False)
            self.history[curr_node] = df
        
        return probabilities