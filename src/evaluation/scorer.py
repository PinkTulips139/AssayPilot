import hashlib
import json
import numpy as np


def score_sealed(receipt, hidden_pairs, labeler, *, online_pairs=None, confirm_fn=None):
    """Trusted runner calls only after Simulation.seal; policies never receive H."""
    payload={k:v for k,v in receipt.items() if k!='sha256'}
    if hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()!=receipt['sha256']:
        raise ValueError('Altered trajectory receipt')
    if set(receipt['candidate_ids'])!=set(hidden_pairs):
        raise ValueError('Hidden bank must exactly match the frozen candidate pool')
    trace=receipt['trace']; selected_all=[t['condition'] for t in trace]
    if len(set(selected_all))!=len(trace) or not set(selected_all).issubset(hidden_pairs):
        raise ValueError('Invalid selected conditions')
    if receipt['confirmation_cost']!=len(trace) or receipt['screening_cost']!=len(hidden_pairs):
        raise ValueError('Cost mismatch')
    rounds=sorted(set(t['round'] for t in trace))
    if rounds!=list(range(len(rounds))) or len(rounds)>13:
        raise ValueError('Invalid round sequence')
    for r in rounds:
        if sum(t['round']==r for t in trace)!=(12 if r==0 else 4):
            raise ValueError('Invalid batch size')
    labels={k:labeler(a,b) for k,(a,b) in hidden_pairs.items()}
    if any(not isinstance(v,(int,np.integer)) or v<0 or v>8 for v in labels.values()):
        raise ValueError('Invalid reference region')
    available=set(labels.values())-{0}; result=[]; previous=0
    for r in sorted(set(t['round'] for t in receipt['trace'])):
        selected=[t['condition'] for t in receipt['trace'] if t['round']<=r]
        values=[labels[k] for k in selected if labels[k]>0]
        counts=np.bincount(values,minlength=9)[1:]; counts=counts[counts>0]
        p=counts/counts.sum() if len(counts) else counts
        online_positive=None; repeated=None
        if online_pairs is not None:
            if confirm_fn is None: raise ValueError('Repeatability needs independent confirmation predicate')
            positive=[k for k in selected if confirm_fn(*online_pairs[k])]
            online_positive=len(positive); repeated=sum(confirm_fn(*hidden_pairs[k]) for k in positive)
        result.append(dict(round=r,confirmation_cost=len(selected),
                           total_cost=receipt['screening_cost']+len(selected)+receipt['reference_cost'],
                           covered_regions=len(set(values)),coverage=len(set(values))/len(available) if available else None,
                           reward=len(set(values))-previous,
                           online_positive=online_positive,repeat_confirmed=repeated,
                           repeatability=repeated/online_positive if online_positive else None,
                           diversity=float(-np.sum(p*np.log(p))/np.log(8)) if len(p) else None))
        previous=len(set(values))
    return result
