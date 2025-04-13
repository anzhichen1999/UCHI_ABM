'''
Only added line that prevents an error or unnecessary calculations when no empty cells are in range
'''
import math
## Using experimental agent type with native "cell" property that saves its current position in cellular grid
from mesa.experimental.cell_space import CellAgent

## Helper function to get distance between two cells
def get_distance(cell_1, cell_2):
    x1, y1 = cell_1.coordinate
    x2, y2 = cell_2.coordinate
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx**2 + dy**2)

class SugarAgent(CellAgent):
    ## Initiate agent, inherit model property from parent class
    def __init__(self, model, cell, sugar=0, metabolism=0, vision=0):
        super().__init__(model)
        self.cell = cell
        self.sugar = sugar
        self.metabolism = metabolism
        self.vision = vision

    ## Define movement action
    def move(self):
        possibles = [
            cell
            for cell in self.cell.get_neighborhood(self.vision, include_center=True)
            if cell.is_empty
        ]
        if not possibles:
            return  # NEW: If no empty cells available, do nothing and skip movement

        sugar_values = [cell.sugar for cell in possibles]
        max_sugar = max(sugar_values)
        candidates_index = [
            i for i, val in enumerate(sugar_values) if math.isclose(val, max_sugar)
        ]
        candidates = [possibles[i] for i in candidates_index]
        min_dist = min(get_distance(self.cell, c) for c in candidates)
        final_candidates = [
            c for c in candidates
            if math.isclose(get_distance(self.cell, c), min_dist, rel_tol=1e-02)
        ]
        self.cell = self.random.choice(final_candidates)

    ## Consume sugar in current cell, then pay metabolic cost
    def gather_and_eat(self):
        self.sugar += self.cell.sugar
        self.cell.sugar = 0
        self.sugar -= self.metabolism

    ## If an agent has zero or negative sugar, remove it from the model
    def see_if_die(self):
        if self.sugar <= 0:
            self.remove()

