"""Four specified diagnostic cuts; no weight search and no changes to v1."""
from collections import Counter
import numpy as np
from .selector import QACS, NeighborEvidence

WEIGHTS={
    'QACS-full':(1.,.25,.25,1.),
    'QACS-no-repeatability':(1.,0.,.25,1.),
    'QACS-no-batch':(1.,.25,0.,1.),
    'QACS-coverage-only':(1.,0.,0.,0.),
}


class AblationQACS(QACS):
    def __init__(self,*args,variant,**kwargs):
        super().__init__(*args,**kwargs)
        self.variant=variant; self.weights=WEIGHTS[variant]

    def select(self,view,size=4):
        evidence=NeighborEvidence(self.history,view,self.labeler,self.confirm_fn)
        estimates={k:evidence.estimate(view.screen[k],view.compounds[k]) for k in view.candidates}
        q=np.zeros(8)
        for k,v in view.observed.items():
            label=self.labeler(view.screen[k],v)
            if label:q[label-1]=1
        t=1+(len(view.observed)-12)//4
        counts=Counter(view.compounds[k] for k in view.selected)
        chosen=[]; self.diagnostics=[]
        for position in range(size):
            legal=[k for k in view.candidates if k not in chosen and counts[view.compounds[k]]<2]
            if not legal:break
            values={}
            for k in legal:
                p,r,u=estimates[k]; gain=float(p[1:]@(1-q)); penalty=self.risk(view.screen[k]); beta=.2/np.sqrt(t)
                wc,wr,wb,we=self.weights
                score=wc*gain+wr*r-wb*penalty+we*beta*u
                values[k]=dict(coverage_gain=gain,repeatability_gain=r,batch_penalty=penalty,
                               uncertainty=u,exploration_weight=float(beta),score=float(score))
            k=min(legal,key=lambda k:(-values[k]['score'],k))
            self.diagnostics.append(dict(condition=k,round=t,batch_position=position,**values[k]))
            chosen.append(k); counts[view.compounds[k]]+=1
            q=q+(1-q)*estimates[k][0][1:]
        return chosen
