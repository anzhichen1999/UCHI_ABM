'''
def calc_wealth_distribution(...): New method that produces a dictionary (bin_center → count) for offline or custom-plotted histograms.
tax_threshold and tax_rate: Added parameters for progressive taxation.
apply_progressive_taxation(...): Newly introduced method that collects tax from agents above tax_threshold and redistributes it evenly.
self.datacollector line updated to collect WealthDist in addition to Gini.
'''
from pathlib import Path
import numpy as np
import mesa
from agents import SugarAgent
from mesa.experimental.cell_space import OrthogonalVonNeumannGrid
from mesa.experimental.cell_space.property_layer import PropertyLayer

class SugarScapeModel(mesa.Model):
    # Helper function to calculate the absolute Gini coefficient (measuring inequality)
    def calc_gini(self):
        agent_sugars = np.array([a.sugar for a in self.agents])
        if len(agent_sugars) == 0:
            return 0
        diffs = np.abs(agent_sugars[:, None] - agent_sugars)
        return np.sum(diffs) / (2 * len(agent_sugars) ** 2)

    ## MODIFICATION: New function to calculate distribution of sugar
    def calc_wealth_distribution(self):
        """
        Returns a histogram-like dictionary mapping
        midpoint of bins -> count of agents in that bin.
        This is used to visualize how wealth is distributed.
        """
        agent_sugars = [a.sugar for a in self.agents]
        if len(agent_sugars) == 0:
            return {}
        counts, bin_edges = np.histogram(agent_sugars, bins=10, range=(0, 100))
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        return dict(zip(bin_centers, counts))
        # NEW: This function provides a dictionary that can be used offline
        # or with a custom histogram plot. It won't work as a direct line plot.

    ## Initialize the model with parameters
    def __init__(
        self,
        width=50,
        height=50,
        initial_population=200,
        endowment_min=25,
        endowment_max=70,
        metabolism_min=1,
        metabolism_max=5,
        vision_min=1,
        vision_max=5,
        seed=None,
        ## MODIFICATION: New progressive taxation parameters
        tax_threshold=50,
        tax_rate=0.1
    ):
        super().__init__(seed=seed)

        # MODIFICATION: Store the new taxation parameters
        self.tax_threshold = tax_threshold  # NEW: sugar level above which agents are taxed
        self.tax_rate = tax_rate           # NEW: fraction of sugar above threshold taken as tax

        # Create the grid (Orthogonal Von Neumann)
        self.grid = OrthogonalVonNeumannGrid(
            (self.width, self.height), torus=False, random=self.random
        )

        # Set up a data collector to record metrics at each step
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Gini": self.calc_gini,
                ## MODIFICATION: Collect distribution data each step
                "WealthDist": self.calc_wealth_distribution,
            },
        )
        # NEW: "WealthDist" is stored here as a dictionary for offline usage.
        # It cannot be line-plotted in default Mesa.

        # Load initial sugar distribution
        self.sugar_distribution = np.genfromtxt(Path(__file__).parent / "sugar-map.txt")

        # Add sugar property to the grid
        self.grid.add_property_layer(
            PropertyLayer.from_data("sugar", self.sugar_distribution)
        )

        # Create initial agents
        SugarAgent.create_agents(
            self,
            initial_population,
            self.random.choices(self.grid.all_cells.cells, k=initial_population),
            sugar=self.rng.integers(endowment_min, endowment_max, (initial_population,), endpoint=True),
            metabolism=self.rng.integers(metabolism_min, metabolism_max, (initial_population,), endpoint=True),
            vision=self.rng.integers(vision_min, vision_max, (initial_population,), endpoint=True),
        )

        # Collect initial data
        self.datacollector.collect(self)

    ## MODIFICATION: Function to apply progressive taxation and redistribute the proceeds
    def apply_progressive_taxation(self):
        if len(self.agents) == 0:
            return

        total_tax_collected = 0
        # NEW: For each agent with sugar above threshold, compute tax due
        for agent in self.agents:
            if agent.sugar > self.tax_threshold:
                taxable_amount = agent.sugar - self.tax_threshold
                tax_due = self.tax_rate * taxable_amount
                agent.sugar -= tax_due
                total_tax_collected += tax_due

        # Redistribute the collected tax equally among all agents
        # NEW: The total tax is shared so every agent, even those below threshold, benefit
        if len(self.agents) > 0:
            per_agent_share = total_tax_collected / len(self.agents)
            for agent in self.agents:
                agent.sugar += per_agent_share

    # Define what happens in each simulation step
    def step(self):
        # Sugar grows back at rate of 1 unit per cell, up to max

        # Agent actions
        self.agents.shuffle_do("move")
        self.agents.shuffle_do("gather_and_eat")
        self.agents.shuffle_do("see_if_die")

        # MODIFICATION: Apply progressive taxation each step
        self.apply_progressive_taxation()
        # NEW: The total sugar above threshold is collected and redistributed.

        # Collect data at the end of the step
        self.datacollector.collect(self)
