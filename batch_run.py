"""
batch_run.py – parameter sweep for the Dark-Forest model
-------------------------------------------------------

• Varies *one* focal parameter (here: aggressive_ratio 0.0 … 1.0 by 0.1)
• Runs N independent replications per setting (iterations=20)
• Executes a fixed number of steps (max_steps=200) for each run
• Collects outcome metrics at the final tick
• Saves:
    - batch_results.csv           ← every run, every metric
    - survival_vs_aggr_ratio.png  ← average survival curves

Run from a terminal:  $ python batch_run.py
"""
from __future__ import annotations
import matplotlib.pyplot as plt
import pandas as pd
from mesa.batchrunner import BatchRunner
from model import DarkForestModel   


variable_params = {
    "aggressive_ratio": [round(x * 0.1, 2) for x in range(11)]  
}

fixed_params = dict(
    grid_width   = 50,
    grid_height  = 50,
    num_t1       = 2,  num_t2 = 2,  num_t3 = 2,
    num_t4       = 2,  num_t5 = 2,  num_t100 = 1,
)

def final_alive(model: DarkForestModel) -> int:
    return sum(a.alive for a in model.schedule.agents)

def final_aggr_surv(model: DarkForestModel) -> float:
    df = model.datacollector.get_model_vars_dataframe()
    return df["AggSurvival"].iloc[-1]

def final_peace_surv(model: DarkForestModel) -> float:
    df = model.datacollector.get_model_vars_dataframe()
    return df["PeaceSurvival"].iloc[-1]

model_reporters = {
    "Alive":         final_alive,
    "AggSurvival":   final_aggr_surv,
    "PeaceSurvival": final_peace_surv,
}


batch = BatchRunner(
    DarkForestModel,
    variable_parameters = variable_params,
    fixed_parameters    = fixed_params,
    iterations          = 20,      # replications per setting
    max_steps           = 200,     # ticks per run
    model_reporters     = model_reporters,
    display_progress    = True,
)
batch.run_all()
results = batch.get_model_vars_dataframe()
results.to_csv("batch_results.csv", index=False)
grp = results.groupby("aggressive_ratio").mean()

plt.figure(figsize=(6,4))
plt.plot(grp.index, grp["AggSurvival"],  marker="o", label="Aggressive")
plt.plot(grp.index, grp["PeaceSurvival"], marker="s", label="Peaceful")
plt.xlabel("Initial aggressive ratio")
plt.ylabel("Final survival share")
plt.title("Survival vs. initial aggressive mix\n(20 runs · 200 steps each)")
plt.ylim(0, 1.05)
plt.grid(True, alpha=.3)
plt.legend()
plt.tight_layout()
plt.savefig("survival_vs_aggr_ratio.png", dpi=150)
plt.show()
