from __future__ import annotations
import math
import mesa


class PlanetAgent(mesa.Agent):
    """
    One civilization (“planet”).
      tech_level : int 1‑1000 (continuous)
      aggressive : True  = Dark‑Forest doctrine (red)
                   False = signalling/peaceful (green)
    """
    def __init__(self, uid: int, model: "DarkForestModel",
                 tech_level: int, aggressive: bool):
        super().__init__(uid, model)
        self.tech_level = tech_level
        self.aggressive = aggressive
        self.alive      = True

    # ---------- dynamic radii (scaled linearly with tech) -------------- #
    @property
    def detection_radius(self) -> int:
        return int(round(self.model.det_base + self.tech_level * self.model.det_factor))

    @property
    def attack_radius(self) -> int:
        return int(round(self.model.att_base + self.tech_level * self.model.att_factor))

    # ------------------------------------------------------------------- #
    def step(self) -> None:
        if not self.alive:
            return

        # --- steady exponential growth ---------------------------------
        p_growth = (self.model.tech_growth_aggressive
                    if self.aggressive else self.model.tech_growth_peaceful)
        if self.random.random() < p_growth:
            new_level = int(self.tech_level * self.model.tech_exponent)
            if new_level <= self.tech_level:          # guarantee progress
                new_level = self.tech_level + 1
            self.tech_level = min(new_level, 1000)

        # --- occasional tech explosion ---------------------------------
        if self.random.random() < self.model.tech_explosion_prob:
            self.tech_level = min(self.tech_level + self.model.tech_explosion_jump, 1000)

        # --- neighbourhood scan ----------------------------------------
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius=self.detection_radius
        )
        neighbors = [n for n in neighbors if getattr(n, "alive", False)]

        # --- pre‑emptive strike ----------------------------------------
        if self.aggressive and neighbors:
            in_range = [
                n for n in neighbors
                if self._dist(n.pos, self.pos) <= self.attack_radius
            ]
            if in_range:
                self._attack(self.random.choice(in_range))

        # --- placeholder signalling risk -------------------------------
        if (not self.aggressive) and self.random.random() < self.model.signal_prob:
            pass

    # ------------------------------------------------------------------- #
    def _attack(self, target: "PlanetAgent") -> None:
        """Probabilistic combat based on tech difference.
        If attacker wins, annexes ½ of target's tech points."""
        diff  = self.tech_level - target.tech_level
        p_win = 0.5 + diff * self.model.battle_factor
        p_win = max(0.0, min(1.0, p_win))            # clamp to [0,1]

        if self.random.random() < p_win:
            # attacker wins – annex half of the victim's tech
            annex = target.tech_level // 2
            self.tech_level = min(self.tech_level + annex, 1000)

            target.alive = False
            self.model.grid.remove_agent(target)
            self.model.schedule.remove(target)
        else:
            # defender survives, becomes aggressive + slight jump
            target.aggressive = True
            target.tech_level = min(target.tech_level + 5, 1000)

    # ------------------------------------------------------------------- #
    @staticmethod
    def _dist(a: tuple[int, int], b: tuple[int, int]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])


