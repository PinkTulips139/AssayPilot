import numpy as np
from sklearn.cluster import KMeans


def confirmed(a, b, threshold):
    if not np.isfinite(a).all() or not np.isfinite(b).all(): return False
    denominator = np.linalg.norm(a)*np.linalg.norm(b)
    return bool(denominator > 0 and np.sqrt(np.mean(a*a)) > threshold
                and np.sqrt(np.mean(b*b)) > threshold and np.dot(a,b)/denominator >= .5)


class ReferenceRegions:
    def __init__(self, threshold): self.threshold = threshold

    def fit(self, pairs, *, split):
        if split != 'development': raise ValueError('Reference fit only on development')
        means = np.array([(a+b)/2 for a,b in pairs if confirmed(a,b,self.threshold)])
        if len(means) < 40: raise ValueError(f'Need 40 confirmed development pairs; found {len(means)}')
        if len(np.unique(means, axis=0)) < 8: raise ValueError('Fewer than eight distinct references')
        km = KMeans(n_clusters=8, random_state=0, n_init=10).fit(means)
        self.centers = km.cluster_centers_
        self.radius = float(np.quantile(np.linalg.norm(means-self.centers[km.labels_], axis=1), .95))
        return self

    def label(self, a, b):
        if not confirmed(a,b,self.threshold): return 0
        if not hasattr(self, 'centers'): raise ValueError('Reference gate has not passed')
        distances = np.linalg.norm(self.centers-(a+b)/2, axis=1)
        return int(np.argmin(distances)+1) if distances.min() <= self.radius else 0
