# agents.py  – Dark-Forest agents with Annexation, Collaboration
# -----------------------------------------------------------------
from __future__ import annotations
import math
import mesa


class PlanetAgent(mesa.Agent):
    """
    One civilisation (“planet”).

        tech_level : int 1-1000
        aggressive : True  = Dark-Forest doctrine (red)
                     False = signalling / peaceful (green)
    """

    # ─────────────────────────────────────────────────────────────
    def __init__(self, uid: int, model: "DarkForestModel",
                 tech_level: int, aggressive: bool):
        super().__init__(uid, model)
        self.tech_level   = tech_level
        self.aggressive   = aggressive
        self.alive        = True
        self._collab_this_step = False          # avoid double boosting

    # ---------- dynamic radii (scaled linearly with tech) --------
    @property
    def detection_radius(self) -> int:
        return int(round(self.model.det_base + self.tech_level * self.model.det_factor))

    @property
    def attack_radius(self) -> int:
        return int(round(self.model.att_base + self.tech_level * self.model.att_factor))

    # ─────────────────────────────────────────────────────────────
    def step(self) -> None:
        if not self.alive:
            return
        self._collab_this_step = False   # reset per tick

        # --- steady exponential growth --------------------------
        p_growth = (self.model.tech_growth_aggressive
                    if self.aggressive else self.model.tech_growth_peaceful)
        if self.random.random() < p_growth:
            new_level = int(self.tech_level * self.model.tech_exponent)
            if new_level <= self.tech_level:        # guarantee progress
                new_level = self.tech_level + 1
            self.tech_level = min(new_level, 1000)

        # --- occasional tech explosion --------------------------
        if self.random.random() < self.model.tech_explosion_prob:
            self.tech_level = min(self.tech_level + self.model.tech_explosion_jump, 1000)

        # --- neighbourhood scan --------------------------------
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius=self.detection_radius
        )
        neighbors = [n for n in neighbors if getattr(n, "alive", False)]

        # --- pre-emptive strike (Dark-Forest) -------------------
        if self.aggressive and neighbors:
            in_range = [n for n in neighbors
                        if self._dist(n.pos, self.pos) <= self.attack_radius]
            if in_range:
                self._attack(self.random.choice(in_range))

        # --- signal & possible collaboration -------------------
        if (not self.aggressive) and self.random.random() < self.model.signal_prob:

            # ⚠️  1. Aggressive neighbours react **immediately**
            for n in neighbors:
                if n.aggressive and self._dist(n.pos, self.pos) <= n.attack_radius:
                    n._attack(self)                       # may kill self

            # 2. If still alive, attempt peaceful collaboration
            if self.alive:
                peaceful_neighbors = [n for n in neighbors if (not n.aggressive)]
                if peaceful_neighbors:
                    partner = self.random.choice(peaceful_neighbors)
                    self._collaborate(partner)

    # ─────────────────────────────────────────────────────────────
    def _attack(self, target: "PlanetAgent") -> None:
        """Probabilistic combat based on tech difference.
        Winner annexes half of the victim's tech points."""
        if (not self.alive) or (not target.alive):
            return

        diff  = self.tech_level - target.tech_level
        p_win = 0.5 + diff * self.model.battle_factor
        p_win = max(0.0, min(1.0, p_win))

        if self.random.random() < p_win:
            annex = target.tech_level // 2
            self.tech_level = min(self.tech_level + annex, 1000)

            target.alive = False
            self.model.grid.remove_agent(target)
            self.model.schedule.remove(target)
        else:
            target.aggressive = True
            target.tech_level = min(target.tech_level + 5, 1000)

    # ─────────────────────────────────────────────────────────────
    def _collaborate(self, partner: "PlanetAgent") -> None:
        """Mutual tech boost for two peaceful neighbours."""
        if (not partner.alive) or self._collab_this_step or partner._collab_this_step:
            return

        boost_self    = int(self.tech_level    * self.model.collaboration_rate)
        boost_partner = int(partner.tech_level * self.model.collaboration_rate)

        self.tech_level     = min(self.tech_level     + boost_self,    1000)
        partner.tech_level  = min(partner.tech_level  + boost_partner, 1000)

        self._collab_this_step     = True
        partner._collab_this_step  = True

    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def _dist(a: tuple[int, int], b: tuple[int, int]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])



