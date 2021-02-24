from .ant import Ant


class Optimize():
    """TKTK"""
    def __init__(self, coordinates, num_ants,
                 radius=None, 
                 alpha=0.5,
                 evaporation_rate=0.1,
                 deposition_factor=None):
        """All __init__ declarations happend here."""
        self.G = self.make_graph(coordinates, radius=radius)
        if radius:
            self.radius = radius
        else:
            max_dist = max(e[2]["distance"] for e in self.G.edges(data=True))
            self.radius = max_dist + 1  #prevent 0.0 probability

        self.alpha = alpha

        self.ants = [Ant(self.G, self.radius, self.alpha) for _ in range(num_ants)]
        self.evaporation_rate = evaporation_rate
        self.deposition_factor = deposition_factor
        
        self.current_shortest_distance = \
            sum(e[2]["distance"] for e in self.G.edges(data=True))
        self.current_shortest_path = []
        self.iteration_count = 0
        self.iteration_best_history = []
        self.global_best_history = []
        self.unique_paths = []


    # Imported Functions
    from ._ant_colony import make_graph
    from ._ant_colony import optimize, release_ants
    from ._ant_colony import update_pheronome_trails, calculate_ph_amount
    from ._ant_colony import update_solution, convergence_detection