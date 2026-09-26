from collections import Counter
import numpy as np
from src.baselines.selectors import Baseline


class NeighborEvidence:
    """Exact baseline neighbor rule, vectorized distances and one bank per round."""
    def __init__(self, history, view, labeler, confirm_fn):
        rows=list(history)+[(k,view.compounds[k],view.screen[k],labeler(view.screen[k],v),
                             confirm_fn(view.screen[k],v)) for k,v in view.observed.items()]
        self.rows=sorted((r for r in rows if np.isfinite(r[2]).all()),key=lambda r:(r[0],r[1],r[3]))
        self.x=np.array([r[2] for r in self.rows])

    def estimate(self, x, compound):
        selected=[]; seen=set()
        if len(self.rows) and np.isfinite(x).all():
            distance=np.linalg.norm(self.x-x,axis=1)
            for j in np.argsort(distance,kind='stable'):
                row=self.rows[j]
                if row[1]!=compound and row[1] not in seen:
                    seen.add(row[1]); selected.append(row)
                if len(selected)==15: break
        n=len(selected)
        p=(np.bincount([r[3] for r in selected],minlength=9)+1/9)/(n+1)
        repeat=(sum(bool(r[4]) for r in selected)+.5)/(n+1)
        uncertainty=float((1-np.sum(p*p))/(8/9))
        return p,float(repeat),uncertainty


class CachedUncertainty(Baseline):
    """Computational caching only; baseline formula, ties and batch choices unchanged."""
    def select(self,view,size=4):
        history=[tuple(r)+(False,) for r in self.history]
        evidence=NeighborEvidence(history,view,self.labeler,lambda a,b:False)
        self._scores={k:evidence.estimate(view.screen[k],view.compounds[k])[2] for k in view.candidates}
        return super().select(view,size)

    def uncertainty(self,key,view): return self._scores[key]


class QACS:
    def __init__(self,history,labeler,confirm_fn,technical_basis):
        self.history=list(history); self.labeler=labeler; self.confirm_fn=confirm_fn
        self.basis=np.array(technical_basis,copy=True); self.diagnostics=[]

    def risk(self,x):
        if not np.isfinite(x).all(): return 1.0
        denom=float(np.dot(x,x))
        if denom==0 or not len(self.basis): return 0.0
        return float(np.clip(np.sum((self.basis@x)**2)/denom,0,1))

    def select(self,view,size=4):
        evidence=NeighborEvidence(self.history,view,self.labeler,self.confirm_fn)
        estimates={k:evidence.estimate(view.screen[k],view.compounds[k]) for k in view.candidates}
        q=np.zeros(8)
        for k,v in view.observed.items():
            label=self.labeler(view.screen[k],v)
            if label: q[label-1]=1
        round_index=1+(len(view.observed)-12)//4
        beta=.2/np.sqrt(round_index)
        counts=Counter(view.compounds[k] for k in view.selected)
        chosen=[]; self.diagnostics=[]
        for position in range(size):
            legal=[k for k in view.candidates if k not in chosen and counts[view.compounds[k]]<2]
            if not legal: break
            def components(k):
                p,repeat,u=estimates[k]
                gain=float(p[1:]@(1-q)); penalty=self.risk(view.screen[k])
                score=gain+.25*repeat-.25*penalty+beta*u
                return dict(coverage_gain=gain,repeatability_gain=repeat,batch_penalty=penalty,
                            uncertainty=u,exploration_weight=float(beta),score=float(score))
            values={k:components(k) for k in legal}
            k=min(legal,key=lambda k:(-values[k]['score'],k))
            self.diagnostics.append(dict(condition=k,round=round_index,batch_position=position,**values[k]))
            chosen.append(k); counts[view.compounds[k]]+=1
            q=q+(1-q)*estimates[k][0][1:]
        return chosen
