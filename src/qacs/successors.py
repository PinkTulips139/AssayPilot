"""Phase15 fixed designs. No hidden evaluation inputs or tunable weight sums."""
from collections import Counter
import numpy as np
from .selector import QACS, NeighborEvidence


class Successor(QACS):
    def __init__(self, *args, variant, **kwargs):
        super().__init__(*args, **kwargs)
        if variant not in ('QACS-Constrained', 'QACS-Lexicographic'):
            raise ValueError(variant)
        self.variant = variant

    def select(self, view, size=4):
        evidence = NeighborEvidence(self.history, view, self.labeler, self.confirm_fn)
        estimates = {k: evidence.estimate(view.screen[k], view.compounds[k]) for k in view.candidates}
        q = np.zeros(8)
        for k, v in view.observed.items():
            label = self.labeler(view.screen[k], v)
            if label:
                q[label - 1] = 1
        counts = Counter(view.compounds[k] for k in view.selected)
        chosen = []
        self.diagnostics = []
        for position in range(size):
            legal = [k for k in view.candidates if k not in chosen and counts[view.compounds[k]] < 2]
            if not legal:
                break
            gain = {k: float(estimates[k][0][1:] @ (1-q)) for k in legal}
            feasible = [k for k in legal if estimates[k][1] >= .5]
            fallback = False
            if self.variant == 'QACS-Constrained':
                if feasible:
                    k = min(feasible, key=lambda k: (-gain[k], k))
                else:
                    fallback = True
                    k = min(legal, key=lambda k: (-estimates[k][1], -gain[k], k))
            else:
                k = min(legal, key=lambda k: (-gain[k], -estimates[k][1], self.risk(view.screen[k]), k))
            self.diagnostics.append(dict(condition=k, batch_position=position,
                coverage_gain=gain[k], repeatability_gain=estimates[k][1],
                batch_penalty=self.risk(view.screen[k]), feasible_count=len(feasible),
                constraint_fallback=fallback, coverage_ties=sum(v == gain[k] for v in gain.values())))
            chosen.append(k)
            counts[view.compounds[k]] += 1
            q += (1-q) * estimates[k][0][1:]
        return chosen
