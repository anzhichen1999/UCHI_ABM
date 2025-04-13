'''
Newly added model parameters that control progressive taxation.
'''
from model import SugarScapeModel
from mesa.visualization import Slider, SolaraViz, make_plot_component
from mesa.visualization.components.matplotlib_components import make_mpl_space_component

from model import SugarScapeModel
from mesa.visualization import Slider, SolaraViz, make_plot_component
from mesa.visualization.components.matplotlib_components import make_mpl_space_component

def agent_portrayal(agent):
    return {
        "marker": "o",
        "color": "red",
        "size": 20,
    }

propertylayer_portrayal = {
    "sugar": {
        "color": "yellow",
        "alpha": 0.8,
        "colorbar": True,
        "vmin": 0,
        "vmax": 10,
    },
}

sugarscape_space = make_mpl_space_component(
    agent_portrayal=agent_portrayal,
    propertylayer_portrayal=propertylayer_portrayal,
    post_process=None,
    draw_grid=False,
)

GiniPlot = make_plot_component("Gini")

model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": 50,
    "height": 50,
    "initial_population": Slider("Initial Population", value=200, min=50, max=500, step=10),
    "endowment_min": Slider("Min Initial Endowment", value=25, min=5, max=30, step=1),
    "endowment_max": Slider("Max Initial Endowment", value=50, min=30, max=100, step=1),
    "metabolism_min": Slider("Min Metabolism", value=1, min=1, max=3, step=1),
    "metabolism_max": Slider("Max Metabolism", value=5, min=3, max=8, step=1),
    "vision_min": Slider("Min Vision", value=1, min=1, max=3, step=1),
    "vision_max": Slider("Max Vision", value=5, min=3, max=8, step=1),

    # Progressive Taxation
    "tax_threshold": Slider("Tax Threshold", value=50, min=0, max=200, step=10),
    "tax_rate": Slider("Tax Rate", value=0.1, min=0.0, max=0.5, step=0.01),
}
# NEW: The two lines above add adjustable parameters for progressive taxation:
# 'tax_threshold' = the sugar level above which agents are taxed
# 'tax_rate'      = the fraction of sugar above threshold to be taxed

model = SugarScapeModel()

page = SolaraViz(
    model,
    components=[
        sugarscape_space,
        GiniPlot,
    ],
    model_params=model_params,
    name="Sugarscape",
    play_interval=150,
)

page
