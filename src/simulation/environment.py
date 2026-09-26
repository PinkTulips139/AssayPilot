from dataclasses import dataclass
from types import MappingProxyType
from collections import Counter
import hashlib
import json
import numpy as np


@dataclass(frozen=True)
class PolicyView:
    screen: dict
    compounds: dict
    observed: dict
    candidates: tuple
    selected: tuple


class Simulation:
    """Runner owns environment. Policies receive copies through view(), never self."""
    def __init__(self, screen, confirmation, compounds, *, seed=0, reference_cost=0):
        if set(screen) != set(confirmation) or set(screen) != set(compounds):
            raise ValueError('Condition bank mismatch')
        self._screen = {k: np.array(v, dtype=float, copy=True) for k,v in screen.items()}
        self._confirmation = {k: np.array(v, dtype=float, copy=True) for k,v in confirmation.items()}
        self._compounds = dict(compounds); self.observed = {}; self.trace = []
        self.round = 0; self.sealed = False; self.reference_cost = int(reference_cost)
        rng = np.random.default_rng(seed)
        groups = sorted(set(compounds.values()))
        if len(groups) < 12:
            raise ValueError('At least 12 compounds required')
        initial = []
        for c in rng.choice(groups, size=12, replace=False):
            initial.append(str(rng.choice(sorted(k for k in screen if compounds[k] == c))))
        self._reveal(initial, 0)

    def _reveal(self, ids, round_index):
        for k in ids:
            v = self._confirmation[k].copy()
            self.observed[k] = v
            self.trace.append(dict(condition=k, round=round_index, success=bool(np.isfinite(v).all())))

    def view(self):
        counts = Counter(self._compounds[k] for k in self.observed)
        candidates = tuple(sorted(k for k in self._screen if k not in self.observed and counts[self._compounds[k]] < 2))
        def copies(d):
            result = {k:v.copy() for k,v in d.items()}
            for v in result.values(): v.flags.writeable = False
            return MappingProxyType(result)
        return PolicyView(copies(self._screen), MappingProxyType(dict(self._compounds)),
                          copies(self.observed), candidates, tuple(self.observed))

    def query(self, ids):
        ids = list(ids)
        if self.sealed or self.round >= 12:
            raise ValueError('Run closed')
        if len(ids) != 4 or len(set(ids)) != 4:
            raise ValueError('Exactly four distinct actions per round')
        view = self.view()
        if not set(ids).issubset(view.candidates):
            raise ValueError('Unauthorized or repeated condition')
        counts = Counter(self._compounds[k] for k in list(self.observed)+ids)
        if max(counts.values()) > 2:
            raise ValueError('Compound dose cap exceeded')
        # No partial update before every action in the batch has passed validation.
        self.round += 1; self._reveal(ids, self.round)
        return {k:self.observed[k].copy() for k in ids}

    def seal(self):
        if self.round < 12:
            counts = Counter(self._compounds[k] for k in self.observed)
            remaining = Counter(self._compounds[k] for k in self.view().candidates)
            capacity = sum(min(n, 2-counts[c]) for c,n in remaining.items())
            if capacity >= 4:
                raise ValueError('Cannot seal before full budget or pool exhaustion')
        self.sealed = True
        payload = dict(trace=self.trace, screening_cost=len(self._screen),
                       confirmation_cost=len(self.observed), reference_cost=self.reference_cost,
                       candidate_ids=sorted(self._screen))
        raw = json.dumps(payload, sort_keys=True).encode()
        return dict(payload, sha256=hashlib.sha256(raw).hexdigest())
