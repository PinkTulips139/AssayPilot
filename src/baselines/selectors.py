from collections import Counter
import numpy as np


class Baseline:
    def __init__(self, method, seed=0, history=(), labeler=None):
        if method not in ('random', 'greedy', 'uncertainty', 'diversity'): raise ValueError(method)
        self.method=method; self.rng=np.random.default_rng(seed)
        # history = (condition, compound, SCREEN representation, online-pair label)
        self.history=list(history); self.labeler=labeler

    def uncertainty(self, key, view):
        if self.labeler is None: raise ValueError('Uncertainty requires a validated reference labeler')
        records=self.history+[(k,view.compounds[k],view.screen[k],self.labeler(view.screen[k],v))
                              for k,v in view.observed.items()]
        target=view.screen[key]; neighbors=[]; used=set()
        if np.isfinite(target).all():
            for k,c,x,label in records:
                if c != view.compounds[key] and np.isfinite(x).all():
                    neighbors.append((float(np.linalg.norm(x-target)),k,c,int(label)))
        labels=[]
        for _,k,c,label in sorted(neighbors):
            if c not in used:
                used.add(c); labels.append(label)
            if len(labels)==15: break
        p=(np.bincount(labels,minlength=9)+1/9)/(len(labels)+1)
        return float((1-np.sum(p*p))/(8/9))

    def select(self, view, size=4):
        chosen=[]; counts=Counter(view.compounds[k] for k in view.selected)
        for _ in range(size):
            legal=[k for k in view.candidates if k not in chosen and counts[view.compounds[k]]<2]
            if not legal: break
            if self.method=='random': k=str(self.rng.choice(legal))
            else:
                def score(k):
                    x=view.screen[k]
                    if self.method=='uncertainty': return self.uncertainty(k,view)
                    if not np.isfinite(x).all(): return -np.inf
                    if self.method=='greedy': return float(np.sqrt(np.mean(x*x)))
                    refs=[view.screen[j] for j in list(view.selected)+chosen if np.isfinite(view.screen[j]).all()]
                    return min(float(np.linalg.norm(x-r)) for r in refs) if refs else 0.0
                k=min(legal,key=lambda k:(-score(k),k))
            chosen.append(k); counts[view.compounds[k]]+=1
        return chosen
