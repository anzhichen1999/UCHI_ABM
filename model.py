# model.py  – Dark-Forest model with Annexation **and** Collaboration
from __future__ import annotations
import mesa
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import PlanetAgent


class DarkForestModel(mesa.Model):
    """
    Continuous-tech Dark-Forest simulation featuring:
      • steady & explosive tech growth
      • annexation combat between aggressors and others
      • voluntary collaboration among peaceful neighbours
    """

    def __init__(
        self,
        # ── grid dimensions ───────────────────────────────────────────
        grid_width: int = 50,
        grid_height: int = 50,
        # ── starting populations (0-5 of each tech band) ─────────────
        num_t1: int = 2, num_t2: int = 2,
        num_t3: int = 2, num_t4: int = 2,
        num_t5: int = 2, num_t100: int = 1,
        aggressive_ratio: float = 0.5,
        # ── tech dynamics ────────────────────────────────────────────
        tech_growth_aggressive: float = 0.02,
        tech_growth_peaceful:   float = 0.01,
        tech_exponent:          float = 1.10,
        tech_explosion_prob:    float = 0.003,
        tech_explosion_jump:    int = 50,
        # ── battle scaling ───────────────────────────────────────────
        battle_factor: float = 0.01,
        # ── signalling & collaboration ───────────────────────────────
        signal_prob: float = 0.10,
        collaboration_rate: float = 5,          # GUI passes “percent”
        # ── detection / attack scaling ───────────────────────────────
        det_base: float = 3.0,  det_factor: float = 0.02,
        att_base: float = 2.0,  att_factor: float = 0.015,
    ):
        super().__init__()

        # store parameters for agents
        self.det_base, self.det_factor = det_base, det_factor
        self.att_base, self.att_factor = att_base, att_factor
        self.tech_growth_aggressive = tech_growth_aggressive
        self.tech_growth_peaceful   = tech_growth_peaceful
        self.tech_exponent          = tech_exponent
        self.tech_explosion_prob    = tech_explosion_prob
        self.tech_explosion_jump    = tech_explosion_jump
        self.battle_factor          = battle_factor
        self.signal_prob            = signal_prob
        self.collaboration_rate     = collaboration_rate / 100.0  # → 0-0.50

        # space & scheduler
        self.grid     = MultiGrid(grid_width, grid_height, torus=False)
        self.schedule = mesa.time.RandomActivation(self)

        # ─────────────────────── spawn civilizations ────────────────
        bands = [(1, num_t1), (2, num_t2), (3, num_t3),
                 (4, num_t4), (5, num_t5), (100, num_t100)]
        uid = 0
        for tech_val, count in bands:
            for _ in range(count):
                aggressive = self.random.random() < aggressive_ratio
                agent = PlanetAgent(uid, self,
                                    tech_level=tech_val,
                                    aggressive=aggressive)
                uid += 1
                self.schedule.add(agent)

                # random empty placement
                x, y = self.random.randrange(grid_width), self.random.randrange(grid_height)
                while not self.grid.is_cell_empty((x, y)):
                    x, y = self.random.randrange(grid_width), self.random.randrange(grid_height)
                self.grid.place_agent(agent, (x, y))

        # ─────────────────────── survival baselines ─────────────────
        self.initial_aggressive_ids = {
            a.unique_id for a in self.schedule.agents if a.aggressive
        }
        self.initial_peaceful_ids = {
            a.unique_id for a in self.schedule.agents if not a.aggressive
        }

        self.initial_aggressive = len(self.initial_aggressive_ids)
        self.initial_peaceful   = len(self.initial_peaceful_ids)

        # ─────────────────────── data collection ────────────────────
        self.datacollector = DataCollector(
            model_reporters={
                # basic counts
                "Alive": lambda m: sum(a.alive for a in m.schedule.agents),
                "Aggressors": lambda m: sum(a.alive and a.aggressive
                                            for a in m.schedule.agents),
                # founding-cohort survival shares
                "AggSurvival": lambda m:
                    (sum(a.alive and (a.unique_id in m.initial_aggressive_ids)
                         for a in m.schedule.agents) / m.initial_aggressive)
                    if m.initial_aggressive else 0,
                "PeaceSurvival": lambda m:
                    (sum(a.alive and (a.unique_id in m.initial_peaceful_ids)
                         for a in m.schedule.agents) / m.initial_peaceful)
                    if m.initial_peaceful else 0,
            }
        )

    # ───────────────────────── main tick ─────────────────────────────
    def step(self) -> None:
        self.datacollector.collect(self)
        self.schedule.step()

