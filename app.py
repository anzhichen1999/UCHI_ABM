from __future__ import annotations
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import Slider
from model import DarkForestModel


# ------------------------------------------------------------------- #
def portrayal(agent) -> dict | None:
    if not agent.alive:
        return None
    col = "red" if agent.aggressive else "green"
    size = 2 + int(agent.tech_level ** 0.3 / 2)   # mild log scaling
    return {"Shape": "circle", "Color": col, "r": size,
            "Filled": "true", "Layer": 0}


# ------------------------------------------------------------------- #
#  Web‑UI sliders
# ------------------------------------------------------------------- #
model_params = {
    # grid size
    "grid_width":  Slider("Grid width", 50, 20, 100, 5),
    "grid_height": Slider("Grid height", 50, 20, 100, 5),

    # initial counts 0‑5 each
    "num_t1":   Slider("# at tech 1",   2, 0, 5, 1),
    "num_t2":   Slider("# at tech 2",   2, 0, 5, 1),
    "num_t3":   Slider("# at tech 3",   2, 0, 5, 1),
    "num_t4":   Slider("# at tech 4",   2, 0, 5, 1),
    "num_t5":   Slider("# at tech 5",   2, 0, 5, 1),
    "num_t100": Slider("# at tech 100", 1, 0, 5, 1),

    # initial strategy mix
    "aggressive_ratio": Slider("Aggressive fraction", 0.5, 0.0, 1.0, 0.05),

    # tech dynamics
    "tech_growth_aggressive": Slider("Growth p(aggr)", 0.02, 0.0, 0.2, 0.005),
    "tech_growth_peaceful":   Slider("Growth p(peace)", 0.01, 0.0, 0.2, 0.005),
    "tech_exponent":          Slider("Tech exponent", 1.10, 1.00, 1.30, 0.01),
    "tech_explosion_prob":    Slider("Explosion prob", 0.003, 0.0, 0.05, 0.001),
    "tech_explosion_jump":    Slider("+Tech on explosion", 50, 10, 200, 10),

    # combat scaling
    "battle_factor": Slider("Battle factor / tech diff", 0.01, 0.0, 0.05, 0.002),

    # signalling
    "signal_prob": Slider("Signal p(peaceful)", 0.10, 0.0, 1.0, 0.05),

    # detection/attack scaling
    "det_base":   Slider("Det base",   3.0, 0.0, 10.0, 0.5),
    "det_factor": Slider("Det factor", 0.02, 0.0, 0.05, 0.002),
    "att_base":   Slider("Att base",   2.0, 0.0, 10.0, 0.5),
    "att_factor": Slider("Att factor", 0.015, 0.0, 0.05, 0.002),
}

# visual modules
grid = CanvasGrid(portrayal, 50, 50, 500, 500)

chart_counts = ChartModule([
    {"Label": "Alive",      "Color": "blue"},
    {"Label": "Aggressors", "Color": "red"},
])

chart_survival = ChartModule([
    {"Label": "AggSurvival",   "Color": "red"},
    {"Label": "PeaceSurvival", "Color": "green"},
], data_collector_name="datacollector")

# server
server = ModularServer(
    DarkForestModel,
    [grid, chart_counts, chart_survival],
    "Dark Forest – Annexation",
    model_params
)

if __name__ == "__main__":
    server.port = 8521
    server.launch()
